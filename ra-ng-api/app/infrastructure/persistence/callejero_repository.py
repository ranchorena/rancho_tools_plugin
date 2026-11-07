"""Callejero, tramos y recorrido con pgRouting. La geometría de la red está en EPSG:5347."""

from __future__ import annotations

import json

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.domain.geo.coordenadas import DISTANCIA_MAXIMA_RED
from app.infrastructure.persistence.models import Tramo
from app.infrastructure.serialization import fila_a_dict


class CallejeroRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._schema = settings.db_schema

    def buscar_tramo(self, nombre_calle: str, altura: int) -> dict | None:
        # El callejero guarda "Av Italia"; quien busca suele escribir "Italia 50".
        # Primero el nombre exacto. Si no hay tramo, el nombre al final del de la calle.
        nombre = func.upper(nombre_calle)
        calle = func.upper(Tramo.calle)
        misma_vereda = func.mod(Tramo.desde, 2) == (altura % 2)
        consulta = (
            select(
                Tramo.id,
                Tramo.calle,
                Tramo.desde,
                Tramo.hasta,
                func.ST_AsGeoJSON(func.ST_Transform(func.ST_Centroid(Tramo.geometry), 4326)).label(
                    "centroide_geojson"
                ),
            )
            .where(Tramo.desde <= altura, altura <= Tramo.hasta)
            .order_by(misma_vereda.desc(), func.length(Tramo.calle))
        )
        fila = self._session.execute(consulta.where(calle == nombre)).first()
        if fila is None:
            fila = self._session.execute(consulta.where(calle.like("% " + nombre_calle))).first()
        return fila_a_dict(fila)

    def tramo_cercano(self, punto: dict) -> tuple[int, float] | None:
        punto_sql = "ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 5347)"
        tramo = self._session.execute(
            text(
                f"""
                SELECT id, ST_Distance(the_geom, {punto_sql}) AS distancia,
                       ST_LineLocatePoint(the_geom, {punto_sql}) AS fraccion
                FROM {self._schema}.callejero
                WHERE source IS NOT NULL AND target IS NOT NULL
                ORDER BY the_geom <-> {punto_sql}
                LIMIT 1
                """
            ),
            {"lon": punto["longitud"], "lat": punto["latitud"]},
        ).first()
        if tramo is None or tramo.distancia > DISTANCIA_MAXIMA_RED:
            return None
        return int(tramo.id), float(tramo.fraccion)

    def cliente_mas_cercano(self, tramo_origen: tuple[int, float]) -> int | None:
        tramo_o, fraccion_o = tramo_origen
        # pid 1 es el origen; cada cliente usa pid = id + 1 para no chocar con él.
        clientes_sql = f"""
            SELECT c.id + 1 AS pid, e.id AS edge_id, ST_LineLocatePoint(e.the_geom, c.geometria) AS fraction
            FROM {self._schema}.clientes c
            CROSS JOIN LATERAL (
                SELECT id, the_geom FROM {self._schema}.callejero
                WHERE source IS NOT NULL AND target IS NOT NULL
                ORDER BY the_geom <-> c.geometria
                LIMIT 1
            ) e
            WHERE c.tiene_pedido = 1 AND c.geometria IS NOT NULL
              AND ST_DWithin(e.the_geom, c.geometria, {DISTANCIA_MAXIMA_RED})
        """
        puntos_sql = f"""
            SELECT 1 AS pid, {tramo_o} AS edge_id, {fraccion_o!r}::float AS fraction
            UNION ALL {clientes_sql}
        """
        destinos = [-int(fila.pid) for fila in self._session.execute(text(clientes_sql))]
        if not destinos:
            return None
        fila = self._session.execute(
            text(
                """
                SELECT -end_pid - 1 AS id_cliente, max(agg_cost) AS costo
                FROM public.pgr_withPoints(CAST(:aristas AS text), CAST(:puntos AS text), -1,
                                           CAST(:destinos AS bigint[]),
                                           directed := true, driving_side := 'b')
                GROUP BY end_pid
                ORDER BY costo
                LIMIT 1
                """
            ),
            {"aristas": self._aristas_sql(), "puntos": puntos_sql, "destinos": destinos},
        ).first()
        return None if fila is None else int(fila.id_cliente)

    def calcular(self, origen: dict, destino: dict, tramos: dict) -> dict | str:
        """Devuelve el recorrido o el código 'not_found'."""
        (tramo_o, fraccion_o), (tramo_d, fraccion_d) = tramos["origen"], tramos["destino"]
        puntos_sql = (
            f"SELECT 1 AS pid, {tramo_o} AS edge_id, {fraccion_o!r}::float AS fraction "
            f"UNION ALL SELECT 2, {tramo_d}, {fraccion_d!r}::float"
        )
        # Los puntos de pgr_withPoints son nodos con id negativo: -1 origen, -2 destino.
        fila = self._session.execute(
            text(
                f"""
                WITH ruta AS (
                    SELECT seq, node, edge, LEAD(node) OVER (ORDER BY seq) AS siguiente
                    FROM public.pgr_withPoints(CAST(:aristas AS text), CAST(:puntos AS text), -1, -2,
                                               directed := true, driving_side := 'b')
                ),
                tramos AS (
                    SELECT r.seq AS orden, c.the_geom AS geom,
                           CASE WHEN r.node = -1 THEN :f_o WHEN r.node = -2 THEN :f_d
                                WHEN r.node = c.source THEN 0.0 ELSE 1.0 END AS desde,
                           CASE WHEN r.siguiente = -1 THEN :f_o WHEN r.siguiente = -2 THEN :f_d
                                WHEN r.siguiente = c.source THEN 0.0 ELSE 1.0 END AS hasta
                    FROM ruta r
                    JOIN {self._schema}.callejero c ON c.id = r.edge
                ),
                partes AS (
                    SELECT 0 AS orden, ST_Transform(ST_SetSRID(ST_MakePoint(:lon_o, :lat_o), 4326), 5347) AS geom
                    UNION ALL
                    SELECT orden, CASE WHEN desde <= hasta THEN ST_LineSubstring(geom, desde, hasta)
                                       ELSE ST_Reverse(ST_LineSubstring(geom, hasta, desde)) END
                    FROM tramos
                    UNION ALL SELECT 2147483647, ST_Transform(ST_SetSRID(ST_MakePoint(:lon_d, :lat_d), 4326), 5347)
                ),
                linea AS (SELECT ST_MakeLine(geom ORDER BY orden) AS geom FROM partes)
                SELECT (SELECT count(*) FROM tramos) AS cantidad,
                       ST_Length(geom) AS distancia,
                       ST_AsGeoJSON(ST_Transform(geom, 4326)) AS geojson
                FROM linea
                """
            ),
            {
                "aristas": self._aristas_sql(),
                "puntos": puntos_sql,
                "f_o": fraccion_o,
                "f_d": fraccion_d,
                "lon_o": origen["longitud"],
                "lat_o": origen["latitud"],
                "lon_d": destino["longitud"],
                "lat_d": destino["latitud"],
            },
        ).first()

        mismo_lugar = tramo_o == tramo_d and abs(fraccion_o - fraccion_d) < 1e-9
        if fila.cantidad == 0 and not mismo_lugar:
            return "not_found"
        return {
            "geometria": json.loads(fila.geojson),
            "distancia_m": int(round(fila.distancia)),
            "tramos": int(fila.cantidad),
        }

    def _aristas_sql(self) -> str:
        # pgRouting descarta las aristas con costo negativo: así se respeta el sentido.
        return f"""
            SELECT id, source, target,
                   CASE WHEN sentido = 1 THEN -1 ELSE ST_Length(the_geom) END AS cost,
                   CASE WHEN sentido = 0 THEN -1 ELSE ST_Length(the_geom) END AS reverse_cost
            FROM {self._schema}.callejero
            WHERE source IS NOT NULL AND target IS NOT NULL
        """
