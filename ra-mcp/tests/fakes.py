"""Transporte HTTP falso para pruebas de ra-mcp."""

from __future__ import annotations

from typing import Any, Callable

from ra_mcp.client import RaApiClient, RaApiConnectionError

Responder = Callable[[str, str, dict | None], tuple[int, Any]]


class RecordingTransport:
    def __init__(self, responder: Responder) -> None:
        self.calls: list[dict] = []
        self._responder = responder

    def __call__(self, method: str, url: str, body: dict | None, timeout: float) -> tuple[int, Any]:
        self.calls.append(
            {"method": method, "url": url, "body": body, "timeout": timeout}
        )
        return self._responder(method, url, body)


def client_con(responder: Responder, base_url: str = "http://raapi.test") -> tuple[RaApiClient, RecordingTransport]:
    transport = RecordingTransport(responder)
    return RaApiClient(base_url, transport=transport), transport


def sin_conexion(method: str, url: str, body: dict | None) -> tuple[int, Any]:
    raise RaApiConnectionError("No se pudo comunicar con raapi: conexión rechazada.")


def cliente(
    id_cliente: int,
    nombre: str,
    direccion: str,
    calle: str,
    altura: int,
) -> dict:
    return {
        "id": id_cliente,
        "nombre": nombre,
        "direccion": direccion,
        "calle": calle,
        "altura": altura,
        "longitud": -58.4,
        "latitud": -34.6,
    }
