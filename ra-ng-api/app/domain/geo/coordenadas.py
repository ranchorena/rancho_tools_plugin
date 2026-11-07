"""Coordenadas REST en EPSG:4326. La persistencia las transforma a EPSG:5347."""

from __future__ import annotations


DISTANCIA_MAXIMA_RED = 300


def parse_coord(valor: str | None, nombre: str, minimo: float, maximo: float) -> float:
    if valor is None or valor.strip() == "":
        raise ValueError(f"La {nombre} es requerida.")
    try:
        numero = float(valor)
    except ValueError as error:
        raise ValueError(f"La {nombre} no es válida.") from error
    if numero < minimo or numero > maximo:
        raise ValueError(f"La {nombre} no es válida.")
    return numero


def punto_pedido(datos: dict) -> tuple[float, float] | None:
    """None conserva la geometría del cliente. ValueError si el par no es válido."""
    if "latitud" not in datos and "longitud" not in datos:
        return None
    latitud = datos.get("latitud")
    longitud = datos.get("longitud")
    if latitud in (None, "") and longitud in (None, ""):
        return None
    try:
        return float(latitud), float(longitud)
    except (TypeError, ValueError) as error:
        raise ValueError("La ubicación del pedido no es válida.") from error


def parse_punto(punto, nombre: str) -> dict:
    if not isinstance(punto, dict):
        raise ValueError(f"El {nombre} es requerido.")
    try:
        latitud = float(punto.get("latitud"))
        longitud = float(punto.get("longitud"))
    except (TypeError, ValueError) as error:
        raise ValueError(f"Las coordenadas del {nombre} no son válidas.") from error
    if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
        raise ValueError(f"Las coordenadas del {nombre} no son válidas.")
    return {"latitud": latitud, "longitud": longitud}
