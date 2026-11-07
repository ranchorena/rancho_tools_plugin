"""Busca calle y altura y devuelve el centroide del tramo en EPSG:4326."""

from __future__ import annotations

import json

from app.application.comun import ejecutar
from app.domain.direcciones.parser import parse_direccion
from app.domain.errors import DomainError
from app.infrastructure.unit_of_work import UnitOfWork


def buscar_direccion(uow: UnitOfWork, datos: dict) -> dict:
    def operacion() -> dict:
        if not datos or "direccion" not in datos:
            raise DomainError(400, "La dirección es requerida")
        calle, altura = parse_direccion(str(datos["direccion"]))
        if not calle or altura is None:
            raise DomainError(
                400,
                "Formato de dirección incorrecto. Se espera 'Nombre de Calle Número' (ej. SARMIENTO 550).",
            )
        fila = uow.callejero.buscar_tramo(calle, altura)
        if not fila:
            raise DomainError(
                404,
                f"Dirección no encontrada: Calle '{calle}' con altura {altura} no existe o altura fuera de rango.",
            )
        geojson = fila.get("centroide_geojson")
        if not geojson:
            raise DomainError(500, "No se pudo calcular el centroide para el tramo encontrado.")
        if isinstance(geojson, str):
            geojson = json.loads(geojson)
        longitud, latitud = geojson["coordinates"]
        return {
            "latitud": latitud,
            "longitud": longitud,
            "tramo_info": {
                "id": fila["id"],
                "nombre_calle": fila["calle"],
                "desde": fila["desde"],
                "hasta": fila["hasta"],
            },
        }

    return ejecutar(uow, operacion, "Error interno del servidor al procesar la búsqueda.")
