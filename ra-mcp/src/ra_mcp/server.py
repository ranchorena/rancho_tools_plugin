"""Servidor FastMCP ra-mcp."""

from __future__ import annotations

import os

from fastmcp import FastMCP

from ra_mcp.client import RaApiClient
from ra_mcp.service import (
    ERROR,
    RAAPI_NOT_CONFIGURED,
    agregar_pedido as agregar_pedido_service,
    buscar_cliente as buscar_cliente_service,
)

BUSCAR_CLIENTE_DESCRIPTION = (
    "Busca clientes por nombre antes de realizar operaciones que requieren identificar a un cliente. "
    "Puede devolver múltiples coincidencias y, en ese caso, el agente debe pedir al usuario que seleccione "
    "el cliente correcto antes de efectuar cambios. "
    "Devuelve status NO_MATCH, ONE_MATCH o MULTIPLE_MATCHES. "
    "Si el status es MULTIPLE_MATCHES, no elijas un cliente ni llames a agregar_pedido: "
    "mostrá id_cliente, nombre, dirección, calle y altura, y esperá la selección. "
    "Las operaciones posteriores usan id_cliente, no el nombre."
)

AGREGAR_PEDIDO_DESCRIPTION = (
    "Registra un pedido para un cliente previamente identificado mediante su id_cliente. "
    "No debe utilizarse si la búsqueda previa devolvió múltiples clientes y el usuario todavía no seleccionó uno. "
    "No acepta el nombre del cliente. "
    "Delega la persistencia en raapi: tiene_pedido pasa a 1, la cantidad de docenas se guarda en cantidad "
    "y nro_pao se guarda en nro_pao. "
    "La respuesta es estructurada; success es false cuando raapi rechaza la operación."
)

INSTRUCCIONES = (
    "Para un pedido expresado por nombre, extraé nombre, cantidad de docenas y nro_pao. "
    "Llamá primero a buscar_cliente. "
    "Con NO_MATCH, informá que no existe coincidencia y no registres el pedido. "
    "Con ONE_MATCH, usá el id_cliente devuelto. "
    "Con MULTIPLE_MATCHES, mostrá todos los candidatos y esperá a que la persona elija uno; "
    "no registres el pedido todavía. "
    "Después llamá a agregar_pedido solo con el id_cliente elegido, la cantidad de docenas y nro_pao."
)

mcp = FastMCP(name="ra-mcp", instructions=INSTRUCCIONES)


def _client_desde_entorno() -> RaApiClient | dict:
    base_url = os.environ.get("RA_API_BASE_URL", "").strip()
    if not base_url:
        return {
            "success": False,
            "error_code": RAAPI_NOT_CONFIGURED,
            "message": "Falta la variable de entorno RA_API_BASE_URL.",
        }
    timeout = _timeout_desde_entorno()
    return RaApiClient(base_url, timeout=timeout)


def _timeout_desde_entorno() -> float:
    raw = os.environ.get("RA_API_TIMEOUT", "").strip()
    if not raw:
        return 30.0
    try:
        timeout = float(raw)
    except ValueError:
        return 30.0
    if timeout <= 0:
        return 30.0
    return timeout


@mcp.tool(
    description=BUSCAR_CLIENTE_DESCRIPTION,
    annotations={
        "title": "Buscar cliente",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def buscar_cliente(nombre: str) -> dict:
    """
    Args:
        nombre: Nombre o fragmento del nombre del cliente. raapi compara en forma parcial y sin distinguir mayúsculas.
    """
    client = _client_desde_entorno()
    if isinstance(client, dict):
        return {**client, "status": ERROR, "clientes": []}
    return buscar_cliente_service(nombre, client)


@mcp.tool(
    description=AGREGAR_PEDIDO_DESCRIPTION,
    annotations={
        "title": "Agregar pedido",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def agregar_pedido(id_cliente: int, cantidad_docenas: float, nro_pao: int) -> dict:
    """
    Args:
        id_cliente: Identificador único del cliente devuelto por buscar_cliente.
        cantidad_docenas: Docenas pedidas. Se persiste en la columna cantidad y debe ser mayor que cero.
        nro_pao: Número de PaO del pedido. Debe ser un entero positivo.
    """
    client = _client_desde_entorno()
    if isinstance(client, dict):
        return client
    return agregar_pedido_service(id_cliente, cantidad_docenas, nro_pao, client)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
