"""Pedidos de un cliente, historial y el alta que acompaña a una actualización."""

from __future__ import annotations

import datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.infrastructure.persistence.models import Cliente, Pedido
from app.infrastructure.serialization import fila_a_dict


class PedidoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def de_fecha(self, cliente_id: int, fecha: datetime.date) -> dict | None:
        inicio = datetime.datetime.combine(fecha, datetime.time.min)
        fin = inicio + datetime.timedelta(days=1)
        consulta = (
            select(
                Pedido.id_pedido.label("id"),
                Pedido.fecha,
                Pedido.cantidad,
                Pedido.direccion,
                Pedido.calle,
                Pedido.altura,
                Pedido.nro_pao,
                Pedido.observaciones.label("observacion"),
                func.ST_X(func.ST_Transform(Pedido.geometry, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Pedido.geometry, 4326)).label("latitud"),
            )
            .where(Pedido.id_cliente == cliente_id, Pedido.fecha >= inicio, Pedido.fecha < fin)
            .order_by(Pedido.id_pedido.desc())
        )
        pedido = fila_a_dict(self._session.execute(consulta).first())
        if pedido is None:
            return None
        if isinstance(pedido.get("fecha"), str):
            pedido["fecha"] = pedido["fecha"][:10]
        return pedido

    def reciente_para_cercano(self, cliente_id: int) -> tuple[int, str] | None:
        hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        futuro = (
            select(Pedido.id_pedido, Pedido.fecha)
            .where(Pedido.id_cliente == cliente_id, Pedido.fecha >= hoy)
            .order_by(Pedido.fecha.asc(), Pedido.id_pedido.asc())
        )
        fila = self._session.execute(futuro).first()
        if fila is None:
            pasado = (
                select(Pedido.id_pedido, Pedido.fecha)
                .where(Pedido.id_cliente == cliente_id)
                .order_by(Pedido.fecha.desc(), Pedido.id_pedido.desc())
            )
            fila = self._session.execute(pasado).first()
        if fila is None:
            return None
        fecha = fila.fecha
        texto = fecha.date().isoformat() if isinstance(fecha, datetime.datetime) else fecha.isoformat()
        return fila.id_pedido, texto

    def primera_fecha(self) -> datetime.date | None:
        primera = self._session.execute(select(func.min(Pedido.fecha))).scalar()
        if primera is None:
            return None
        return primera.date() if isinstance(primera, datetime.datetime) else primera

    def ultima_fecha(self) -> datetime.date | None:
        ultima = self._session.execute(select(func.max(Pedido.fecha))).scalar()
        if ultima is None:
            return None
        return ultima.date() if isinstance(ultima, datetime.datetime) else ultima

    def historico(self, desde: datetime.date, hasta: datetime.date) -> list[dict]:
        inicio = datetime.datetime.combine(desde, datetime.time.min)
        fin = datetime.datetime.combine(hasta + datetime.timedelta(days=1), datetime.time.min)
        consulta = (
            select(
                Pedido.id_pedido.label("id"),
                Pedido.fecha,
                Pedido.id_cliente,
                Pedido.nombre,
                Pedido.direccion,
                Pedido.cantidad,
                Cliente.telefono,
                Cliente.horario,
                Pedido.nro_pao,
                Cliente.es_regalo,
                Pedido.precio_unitario,
                Pedido.observaciones.label("observacion"),
                func.ST_X(func.ST_Transform(Pedido.geometry, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Pedido.geometry, 4326)).label("latitud"),
            )
            .outerjoin(Cliente, Cliente.id == Pedido.id_cliente)
            .where(Pedido.fecha >= inicio, Pedido.fecha < fin)
            .order_by(Pedido.id_pedido)
        )
        return [fila_a_dict(fila) for fila in self._session.execute(consulta).all()]

    def obtener(self, id_pedido: int) -> Pedido | None:
        return self._session.get(Pedido, id_pedido)

    def conserva_otro_vigente(self, id_cliente: int, id_pedido: int) -> bool:
        hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        consulta = select(Pedido.id_pedido).where(
            Pedido.id_cliente == id_cliente,
            Pedido.id_pedido != id_pedido,
            Pedido.fecha >= hoy,
        )
        return self._session.execute(consulta).first() is not None

    def eliminar(self, pedido: Pedido) -> None:
        self._session.delete(pedido)
        self._session.flush()

    def agregar(self, pedido: Pedido) -> None:
        self._session.add(pedido)
        self._session.flush()

    def guardar(self, datos: dict) -> str:
        """Actualiza el pedido del cliente para esa fecha. Si no existe, lo inserta."""
        inicio = datos["fecha"]
        fin = inicio + datetime.timedelta(days=1)
        existente = self._session.execute(
            select(Pedido.id_pedido)
            .where(
                Pedido.id_cliente == datos["id_cliente"],
                Pedido.fecha >= inicio,
                Pedido.fecha < fin,
            )
            .order_by(Pedido.id_pedido.desc())
        ).first()
        if existente is None:
            if "lon" in datos:
                self._session.execute(
                    text(
                        f"""
                        INSERT INTO {settings.db_schema}.pedido
                        (fecha, id_cliente, nombre, turno, cantidad, direccion, calle, altura, geometry,
                         observaciones, precio_unitario, nro_pao)
                        VALUES
                        (:fecha, :id_cliente, :nombre, :turno, :cantidad, :direccion, :calle, :altura,
                         ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 5347),
                         :observaciones, :precio_unitario, :nro_pao)
                        """
                    ),
                    datos,
                )
            else:
                self._session.add(Pedido(**datos))
            self._session.flush()
            return "Pedido registrado correctamente."

        parametros = {
            "id_pedido": existente[0],
            "fecha": datos["fecha"],
            "id_cliente": datos["id_cliente"],
            "nombre": datos["nombre"],
            "turno": datos["turno"],
            "cantidad": datos["cantidad"],
            "direccion": datos["direccion"],
            "calle": datos["calle"],
            "altura": datos["altura"],
            "observaciones": datos["observaciones"],
            "nro_pao": datos["nro_pao"],
        }
        if "lon" in datos:
            parametros["lon"] = datos["lon"]
            parametros["lat"] = datos["lat"]
            geometry_sql = "ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 5347)"
        else:
            geometry_sql = f"(SELECT geometria FROM {settings.db_schema}.clientes WHERE id = :id_cliente)"
        self._session.execute(
            text(
                f"""
                UPDATE {settings.db_schema}.pedido SET
                    fecha = :fecha,
                    nombre = :nombre,
                    turno = :turno,
                    cantidad = :cantidad,
                    direccion = :direccion,
                    calle = :calle,
                    altura = :altura,
                    observaciones = :observaciones,
                    nro_pao = :nro_pao,
                    geometry = {geometry_sql}
                WHERE id_pedido = :id_pedido
                """
            ),
            parametros,
        )
        return "Pedido actualizado correctamente."
