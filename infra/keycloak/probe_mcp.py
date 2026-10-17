"""Cliente OAuth contra el ra-mcp HTTP ya levantado.

Abre el navegador en el login de Keycloak. El access token que ra-mcp
reenvía a raapi sale de Token Exchange; este script solo muestra el
resultado de buscar_cliente, sin imprimir JWTs.
"""

from __future__ import annotations

import asyncio
import socket

_original = socket.getaddrinfo


def _ipv4(host, port, *args, **kwargs):
    return [item for item in _original(host, port, *args, **kwargs) if item[0] == socket.AF_INET]


socket.getaddrinfo = _ipv4

from fastmcp.client.auth import OAuth
from fastmcp.client.client import Client

URL = "http://localhost:8000/mcp"


async def main() -> None:
    oauth = OAuth(mcp_url=URL, callback_port=9876, callback_timeout=180, client_name="ra-mcp-probe")
    async with Client(URL, auth=oauth) as client:
        resultado = await client.call_tool("buscar_cliente", {"nombre": "Silvia"})
    datos = resultado.data if hasattr(resultado, "data") else resultado
    estado = datos.get("status") if isinstance(datos, dict) else type(datos).__name__
    cantidad = len(datos.get("clientes", [])) if isinstance(datos, dict) else None
    print({"status": estado, "cantidad": cantidad})


if __name__ == "__main__":
    asyncio.run(main())
