"""Recorrido más corto en metros entre dos puntos, respetando el sentido de los tramos."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.domain.geo.coordenadas import DISTANCIA_MAXIMA_RED, parse_punto
from app.infrastructure.unit_of_work import UnitOfWork


def calcular_ruta(uow: UnitOfWork, datos: dict) -> dict:
    try:
        origen = parse_punto((datos or {}).get("origen"), "origen")
        destino = parse_punto((datos or {}).get("destino"), "destino")
    except ValueError as error:
        raise DomainError(400, str(error)) from error

    def operacion() -> dict:
        tramos = {}
        for rol, punto in (("origen", origen), ("destino", destino)):
            tramo = uow.callejero.tramo_cercano(punto)
            if tramo is None:
                raise DomainError(404, f"El {rol} está a más de {DISTANCIA_MAXIMA_RED} m del callejero.")
            tramos[rol] = tramo
        ruta = uow.callejero.calcular(origen, destino, tramos)
        if ruta == "not_found":
            raise DomainError(404, "No hay recorrido posible entre los puntos elegidos.")
        return ruta

    return ejecutar(uow, operacion, "Error interno del servidor al calcular el recorrido.")
