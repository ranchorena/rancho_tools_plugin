"""OAuth HTTP de ra-mcp.

FastMCP 4.1.0 valida dos tokens distintos:

- El JWT que emite OAuthProxy para Cursor. Su audiencia es la URL del
  recurso, http://localhost:8000/mcp. Lo firma RA_MCP_JWT_SIGNING_KEY.
- El access token upstream de Keycloak, recuperado con get_access_token().
  JWTVerifier exige issuer del realm rancho y audiencia ra-mcp.
  Ese token no se reenvía a raapi: se intercambia por otro con aud=raapi.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from key_value.aio.stores.filetree import FileTreeStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper

from ra_mcp.token_exchange import intercambiar_token

AUDIENCIA_MCP = "ra-mcp"
AUDIENCIA_API = "raapi"


def transporte_http() -> bool:
    return os.environ.get("RA_MCP_TRANSPORT", "stdio").strip().lower() == "http"


def _exigir_entorno(nombre: str) -> str:
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise RuntimeError(f"Falta la variable de entorno {nombre}.")
    return valor


def construir_proxy() -> OAuthProxy:
    issuer = _exigir_entorno("KEYCLOAK_ISSUER").rstrip("/")
    public_url = _exigir_entorno("RA_MCP_PUBLIC_URL").rstrip("/")
    almacenamiento = FernetEncryptionWrapper(
        key_value=FileTreeStore(data_directory=Path.home() / ".ra-mcp" / "oauth"),
        source_material=_exigir_entorno("RA_MCP_OAUTH_STORAGE_KEY"),
        salt="ra-mcp-oauth-storage-v1",
        raise_on_decryption_error=False,
    )
    verifier = JWTVerifier(
        jwks_uri=_exigir_entorno("KEYCLOAK_JWKS_URL"),
        issuer=issuer,
        audience=AUDIENCIA_MCP,
    )
    return OAuthProxy(
        upstream_authorization_endpoint=f"{issuer}/protocol/openid-connect/auth",
        upstream_token_endpoint=f"{issuer}/protocol/openid-connect/token",
        upstream_client_id=os.environ.get("KEYCLOAK_CLIENT_ID", "ra-mcp").strip() or "ra-mcp",
        upstream_client_secret=_exigir_entorno("KEYCLOAK_CLIENT_SECRET"),
        token_verifier=verifier,
        base_url=public_url,
        redirect_path="/auth/callback",
        jwt_signing_key=_exigir_entorno("RA_MCP_JWT_SIGNING_KEY"),
        client_storage=almacenamiento,
        forward_pkce=True,
        forward_resource=False,
        allowed_client_redirect_uris=[
            "http://localhost:*",
            "http://127.0.0.1:*",
            "cursor://anysphere.cursor-mcp/*",
            "https://www.cursor.com/agents/mcp/oauth/callback",
        ],
    )


def token_para_raapi(subject_token: str) -> str:
    issuer = _exigir_entorno("KEYCLOAK_ISSUER").rstrip("/")
    return intercambiar_token(
        token_endpoint=f"{issuer}/protocol/openid-connect/token",
        client_id=os.environ.get("KEYCLOAK_CLIENT_ID", "ra-mcp").strip() or "ra-mcp",
        client_secret=_exigir_entorno("KEYCLOAK_CLIENT_SECRET"),
        subject_token=subject_token,
        audience=os.environ.get("RA_API_AUDIENCE", AUDIENCIA_API).strip() or AUDIENCIA_API,
    )
