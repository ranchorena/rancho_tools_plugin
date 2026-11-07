"""Lectura y escritura del agregado Cliente."""

from __future__ import annotations

from sqlalchemy import and_, func, or_, select, text, update
from sqlalchemy.orm import Session

from app.config import settings
from app.infrastructure.persistence.models import Cliente
from app.infrastructure.serialization import fila_a_dict

_COLUMNAS_BUSQUEDA = (
    Cliente.id,
    Cliente.nombre,
    Cliente.direccion,
    Cliente.calle,
    Cliente.altura,
    Cliente.telefono,
    Cliente.tiene_pedido,
    func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
    func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud"),
)


class ClienteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar_por_nombre(self, nombre: str) -> list[dict]:
        consulta = select(*_COLUMNAS_BUSQUEDA).where(
            and_(
                func.lower(Cliente.nombre).like(func.lower(f"%{nombre}%")),
                Cliente.geometria.isnot(None),
            )
        )
        return [fila_a_dict(fila) for fila in self._session.execute(consulta).all()]

    def buscar_por_direccion(self, direccion: str) -> list[dict]:
        consulta = select(*_COLUMNAS_BUSQUEDA).where(
            and_(
                func.lower(Cliente.direccion).like(func.lower(f"%{direccion}%")),
                Cliente.geometria.isnot(None),
            )
        )
        return [fila_a_dict(fila) for fila in self._session.execute(consulta).all()]

    def buscar_por_calle_altura(self, calle: str, altura) -> list[dict]:
        filtros = [
            or_(
                func.lower(Cliente.calle).like(func.lower(f"%{calle}%")),
                func.lower(Cliente.direccion).like(func.lower(f"%{calle}%")),
            ),
            Cliente.geometria.isnot(None),
        ]
        if altura is not None and altura != "":
            try:
                filtros.append(Cliente.altura == int(altura))
            except (TypeError, ValueError):
                pass
        consulta = select(*_COLUMNAS_BUSQUEDA).where(and_(*filtros))
        return [fila_a_dict(fila) for fila in self._session.execute(consulta).all()]

    def obtener(self, cliente_id: int) -> Cliente | None:
        return self._session.get(Cliente, cliente_id)

    def existe(self, cliente_id: int) -> bool:
        consulta = select(Cliente.id).where(Cliente.id == cliente_id)
        return self._session.execute(consulta).first() is not None

    def actualizar(self, cliente_id: int, valores: dict) -> int:
        resultado = self._session.execute(
            update(Cliente).where(Cliente.id == cliente_id).values(**valores)
        )
        return resultado.rowcount or 0

    def insertar(self, datos: dict) -> dict | None:
        consulta = text(
            f"""
            INSERT INTO {settings.db_schema}.clientes
            (nombre, direccion, calle, altura, tiene_pedido, telefono, cantidad, horario,
             nro_pao, observacion, es_regalo, geometria)
            VALUES
            (:nombre, :direccion, :calle, :altura, :tiene_pedido, :telefono, :cantidad, :horario,
             :nro_pao, :observacion, :es_regalo,
             ST_Transform(ST_SetSRID(ST_MakePoint(:longitud, :latitud), 4326), 5347))
            RETURNING id, nombre, direccion, calle, altura,
                      ST_X(ST_Transform(geometria, 4326)) AS longitud,
                      ST_Y(ST_Transform(geometria, 4326)) AS latitud
            """
        )
        return fila_a_dict(self._session.execute(consulta, datos).fetchone())

    def listar_con_pedido(self) -> list[dict]:
        consulta = select(
            Cliente.id,
            Cliente.nombre,
            Cliente.direccion,
            Cliente.calle,
            Cliente.altura,
            Cliente.tiene_pedido,
            Cliente.telefono,
            Cliente.cantidad,
            Cliente.horario,
            Cliente.nro_pao,
            Cliente.observacion,
            Cliente.es_regalo,
            func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
            func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud"),
        ).where(and_(Cliente.tiene_pedido == 1, Cliente.geometria.isnot(None)))
        return [fila_a_dict(fila) for fila in self._session.execute(consulta).all()]

    def hay_pedidos_activos(self) -> bool:
        consulta = select(Cliente.id).where(and_(Cliente.tiene_pedido == 1, Cliente.geometria.isnot(None)))
        return self._session.execute(consulta).first() is not None

    def obtener_para_cercano(self, cliente_id: int) -> dict | None:
        consulta = select(
            Cliente.id,
            Cliente.nombre,
            Cliente.direccion,
            Cliente.calle,
            Cliente.altura,
            Cliente.telefono,
            Cliente.cantidad,
            Cliente.horario,
            Cliente.observacion,
            func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
            func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud"),
        ).where(Cliente.id == cliente_id)
        return fila_a_dict(self._session.execute(consulta).first())

    def quitar_marca_pedido(self, cliente_id: int) -> None:
        self._session.execute(
            update(Cliente)
            .where(Cliente.id == cliente_id)
            .values(tiene_pedido=0, cantidad=1, horario=None, nro_pao=None, es_regalo=0)
        )

    def iniciar_pedidos(self) -> int:
        resultado = self._session.execute(
            update(Cliente)
            .where(Cliente.tiene_pedido == 1)
            .values(tiene_pedido=0, cantidad=1, horario=None, nro_pao=None, es_regalo=0)
        )
        return resultado.rowcount or 0
