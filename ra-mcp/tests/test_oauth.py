import base64
import json

import pytest
from fastmcp.exceptions import AuthorizationError

from ra_mcp.client import RaApiClient
from ra_mcp.http_auth import AUDIENCIA_API, AUDIENCIA_MCP
from ra_mcp.server import _exigir_rol
from ra_mcp.token_exchange import intercambiar_token, solicitud_de_intercambio


def _jwt(payload: dict) -> str:
    cuerpo = json.dumps(payload).encode("utf-8")
    parte = base64.urlsafe_b64encode(cuerpo).decode("ascii").rstrip("=")
    return f"eyJhbGciOiJub25lIn0.{parte}.firma"


def test_la_audiencia_del_proxy_no_es_la_de_raapi():
    assert AUDIENCIA_MCP == "ra-mcp"
    assert AUDIENCIA_API == "raapi"
    assert AUDIENCIA_MCP != AUDIENCIA_API


def test_solicitud_de_token_exchange_filtra_audiencia_raapi():
    subject = _jwt({"aud": ["ra-mcp", "raapi"], "azp": "ra-mcp"})
    solicitud = solicitud_de_intercambio(subject_token=subject, audience="raapi", client_id="ra-mcp")
    assert solicitud["grant_type"] == "urn:ietf:params:oauth:grant-type:token-exchange"
    assert solicitud["subject_token_type"] == "urn:ietf:params:oauth:token-type:access_token"
    assert solicitud["audience"] == "raapi"
    assert solicitud["subject_token"] == subject


def test_el_cliente_envia_solo_el_token_intercambiado():
    subject = _jwt({"aud": "ra-mcp", "azp": "ra-mcp", "sub": "usuario"})
    downstream = _jwt({"aud": "raapi", "azp": "ra-mcp", "sub": "usuario", "resource_access": {"raapi": {"roles": ["clientes:read"]}}})
    vistos = {}

    def transport(url, data):
        vistos["url"] = url
        vistos["body"] = data.decode("utf-8")
        return 200, {"access_token": downstream}

    obtenido = intercambiar_token(
        token_endpoint="http://keycloak.test/token",
        client_id="ra-mcp",
        client_secret="secreto",
        subject_token=subject,
        audience="raapi",
        transport=transport,
    )
    assert obtenido == downstream
    assert subject not in vistos["body"] or "subject_token=" in vistos["body"]
    assert "audience=raapi" in vistos["body"]

    enviados = {}

    def http(method, url, body, timeout, headers=None):
        enviados["headers"] = headers
        return 200, []

    cliente = RaApiClient("http://raapi.test", transport=http, token_provider=lambda: obtenido)
    cliente.buscar_por_nombre("Silvia")
    assert enviados["headers"]["Authorization"] == f"Bearer {downstream}"
    assert subject not in enviados["headers"]["Authorization"]


def test_rechaza_passthrough_del_mismo_token():
    mismo = _jwt({"aud": "raapi"})
    with pytest.raises(RuntimeError, match="mismo token"):
        intercambiar_token(
            token_endpoint="http://keycloak.test/token",
            client_id="ra-mcp",
            client_secret="secreto",
            subject_token=mismo,
            audience="raapi",
            transport=lambda url, data: (200, {"access_token": mismo}),
        )


def test_rol_en_modo_stdio_no_bloquea(monkeypatch):
    monkeypatch.setenv("RA_MCP_TRANSPORT", "stdio")
    _exigir_rol("clientes:read")


def test_buscar_sin_clientes_read_se_rechaza(monkeypatch):
    monkeypatch.setenv("RA_MCP_TRANSPORT", "http")
    monkeypatch.setattr(
        "ra_mcp.server.get_access_token",
        lambda: type("Token", (), {"claims": {"resource_access": {"raapi": {"roles": ["pedidos:write"]}}}, "token": "upstream"})(),
    )
    with pytest.raises(AuthorizationError):
        _exigir_rol("clientes:read")


def test_buscar_con_clientes_read_pasa(monkeypatch):
    monkeypatch.setenv("RA_MCP_TRANSPORT", "http")
    monkeypatch.setattr(
        "ra_mcp.server.get_access_token",
        lambda: type("Token", (), {"claims": {"resource_access": {"raapi": {"roles": ["clientes:read"]}}}, "token": "upstream"})(),
    )
    _exigir_rol("clientes:read")


def test_pedido_sin_write_se_rechaza(monkeypatch):
    monkeypatch.setenv("RA_MCP_TRANSPORT", "http")
    monkeypatch.setattr(
        "ra_mcp.server.get_access_token",
        lambda: type("Token", (), {"claims": {"resource_access": {"raapi": {"roles": ["clientes:read"]}}}, "token": "upstream"})(),
    )
    with pytest.raises(AuthorizationError):
        _exigir_rol("pedidos:write")


def test_pedido_con_write_pasa(monkeypatch):
    monkeypatch.setenv("RA_MCP_TRANSPORT", "http")
    monkeypatch.setattr(
        "ra_mcp.server.get_access_token",
        lambda: type("Token", (), {"claims": {"resource_access": {"raapi": {"roles": ["pedidos:write"]}}}, "token": "upstream"})(),
    )
    _exigir_rol("pedidos:write")
