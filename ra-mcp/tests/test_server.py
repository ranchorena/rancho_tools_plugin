import os

import pytest

from ra_mcp.server import (
    AGREGAR_PEDIDO_DESCRIPTION,
    BUSCAR_CLIENTE_DESCRIPTION,
    agregar_pedido,
    buscar_cliente,
    mcp,
)


def test_descripciones_obligatorias():
    assert "Busca clientes por nombre antes de realizar operaciones que requieren identificar a un cliente." in BUSCAR_CLIENTE_DESCRIPTION
    assert "el agente debe pedir al usuario que seleccione el cliente correcto antes de efectuar cambios" in BUSCAR_CLIENTE_DESCRIPTION
    assert "Registra un pedido para un cliente previamente identificado mediante su id_cliente." in AGREGAR_PEDIDO_DESCRIPTION
    assert "No debe utilizarse si la búsqueda previa devolvió múltiples clientes y el usuario todavía no seleccionó uno." in AGREGAR_PEDIDO_DESCRIPTION


def test_el_servidor_expone_solo_los_dos_tools():
    tools = mcp.list_tools()
    if hasattr(tools, "__await__"):
        import asyncio

        tools = asyncio.run(tools)
    registrados = list(_iterable(tools))
    nombres = sorted(_nombre(tool) for tool in registrados)
    assert nombres == ["agregar_pedido", "buscar_cliente"]
    descripciones = {_nombre(tool): getattr(tool, "description", "") for tool in registrados}
    assert "el agente debe pedir al usuario que seleccione el cliente correcto antes de efectuar cambios" in descripciones["buscar_cliente"]
    assert "el usuario todavía no seleccionó uno" in descripciones["agregar_pedido"]


def test_sin_url_no_hay_direccion_de_desarrollo_implicita(monkeypatch):
    monkeypatch.delenv("RA_API_BASE_URL", raising=False)

    busqueda = buscar_cliente("Silvia")
    pedido = agregar_pedido(145, 2, 3)

    assert busqueda["success"] is False
    assert busqueda["error_code"] == "RAAPI_NOT_CONFIGURED"
    assert busqueda["status"] == "ERROR"
    assert pedido["success"] is False
    assert pedido["error_code"] == "RAAPI_NOT_CONFIGURED"
    assert "localhost" not in busqueda["message"]
    assert os.environ.get("RA_API_BASE_URL", "") == ""


def _iterable(tools):
    if isinstance(tools, dict):
        return tools.values()
    return tools


def _nombre(tool):
    return getattr(tool, "name", None) or tool["name"]
