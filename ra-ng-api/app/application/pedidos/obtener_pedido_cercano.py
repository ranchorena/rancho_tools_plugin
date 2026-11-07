"""Pedido activo de menor recorrido por el callejero desde un punto EPSG:4326."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.domain.geo.coordenadas import DISTANCIA_MAXIMA_RED, parse_coord
from app.infrastructure.unit_of_work import UnitOfWork


def obtener_pedido_cercano(uow: UnitOfWork, latitud_texto: str | None, longitud_texto: str | None) -> dict:
    try:
        latitud = parse_coord(latitud_texto, "latitud", -90, 90)
        longitud = parse_coord(longitud_texto, "longitud", -180, 180)
    except ValueError as error:
        raise DomainError(400, str(error)) from error

    def operacion() -> dict:
        if not uow.clientes.hay_pedidos_activos():
            return {"pedido": None}
        origen = {"latitud": latitud, "longitud": longitud}
        tramo_origen = uow.callejero.tramo_cercano(origen)
        if tramo_origen is None:
            raise DomainError(404, f"La posición está a más de {DISTANCIA_MAXIMA_RED} m del callejero.")
        cliente_id = uow.callejero.cliente_mas_cercano(tramo_origen)
        if cliente_id is None:
            raise DomainError(404, "No hay recorrido posible hasta ningún pedido activo.")
        fila = uow.clientes.obtener_para_cercano(cliente_id)
        destino = {"latitud": fila["latitud"], "longitud": fila["longitud"]}
        tramo_destino = uow.callejero.tramo_cercano(destino)
        if tramo_destino is None:
            raise DomainError(404, f"El destino está a más de {DISTANCIA_MAXIMA_RED} m del callejero.")
        ruta = uow.callejero.calcular(origen, destino, {"origen": tramo_origen, "destino": tramo_destino})
        if ruta == "not_found":
            raise DomainError(404, "No hay recorrido posible entre los puntos elegidos.")
        pedido = dict(fila)
        pedido["distancia"] = ruta["distancia_m"]
        reciente = uow.pedidos.reciente_para_cercano(fila["id"])
        if reciente is None:
            pedido["id_pedido"] = None
            pedido["fecha"] = None
        else:
            pedido["id_pedido"], pedido["fecha"] = reciente
        pedido["observaciones"] = pedido.pop("observacion", None)
        return {"pedido": pedido, "ruta": ruta}

    return ejecutar(uow, operacion, "Error interno del servidor al buscar el pedido más cercano.")
