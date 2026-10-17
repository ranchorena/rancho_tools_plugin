"""Standard Token Exchange V2 hacia la audiencia raapi.

El subject_token es el access token de Keycloak del usuario. El resultado
es el único Bearer que se envía a raapi. No es el JWT interno de FastMCP.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

GRANT = "urn:ietf:params:oauth:grant-type:token-exchange"
TOKEN_TYPE = "urn:ietf:params:oauth:token-type:access_token"

Transport = Callable[[str, bytes], tuple[int, Any]]


def solicitud_de_intercambio(*, subject_token: str, audience: str, client_id: str) -> dict[str, str]:
    return {
        "grant_type": GRANT,
        "subject_token": subject_token,
        "subject_token_type": TOKEN_TYPE,
        "requested_token_type": TOKEN_TYPE,
        "audience": audience,
        "client_id": client_id,
    }


def intercambiar_token(
    *,
    token_endpoint: str,
    client_id: str,
    client_secret: str,
    subject_token: str,
    audience: str,
    transport: Transport | None = None,
) -> str:
    cuerpo = solicitud_de_intercambio(
        subject_token=subject_token,
        audience=audience,
        client_id=client_id,
    )
    cuerpo["client_secret"] = client_secret
    data = urllib.parse.urlencode(cuerpo).encode("utf-8")
    enviar = transport or _urllib
    status, payload = enviar(token_endpoint, data)
    if status >= 400 or not isinstance(payload, dict):
        raise RuntimeError(f"Token Exchange rechazado (HTTP {status}).")
    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError("Token Exchange no devolvió un access token.")
    if access_token == subject_token:
        raise RuntimeError("Token Exchange devolvió el mismo token de entrada.")
    return access_token


def _urllib(url: str, data: bytes) -> tuple[int, Any]:
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
        return error.code, payload
