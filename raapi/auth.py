"""Validación de access tokens de Keycloak para el resource server raapi.

Rechaza cualquier JWT que no tenga audiencia raapi, aunque esté firmado
por el realm rancho. La identidad sale solo de los claims del token.
"""

from __future__ import annotations

import os
from functools import lru_cache

import jwt
from flask import g, jsonify, request
from jwt import PyJWKClient
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidTokenError,
    PyJWTError,
)

ROLES_POR_ENDPOINT = {
    "buscar_clientes_api": "clientes:read",
    "get_clientes_con_pedidos": "clientes:read",
    "get_pedidos_historico": "clientes:read",
    "get_pedido_de_fecha": "clientes:read",
    "get_pedido_cercano": "clientes:read",
    "actualizar_cliente_api": "pedidos:write",
    "eliminar_pedido_api": "pedidos:write",
    "iniciar_pedidos_api": "pedidos:write",
}

RUTAS_PUBLICAS = {"/", "/health", "/apispec.json"}
PREFIJOS_PUBLICOS = ("/swagger", "/flasgger_static")


class AuthError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def configuracion() -> dict:
    issuer = os.environ.get("KEYCLOAK_ISSUER", "").strip()
    jwks_url = os.environ.get("KEYCLOAK_JWKS_URL", "").strip()
    audience = os.environ.get("RA_API_AUDIENCE", "raapi").strip() or "raapi"
    if not issuer or not jwks_url:
        raise AuthError(500, "La validación de tokens no está configurada.")
    return {"issuer": issuer, "jwks_url": jwks_url, "audience": audience}


@lru_cache(maxsize=4)
def _cliente_jwks(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=300)


def decodificar_token(token: str, *, key_resolver=None) -> dict:
    config = configuracion()
    try:
        if key_resolver is None:
            clave = _cliente_jwks(config["jwks_url"]).get_signing_key_from_jwt(token).key
        else:
            clave = key_resolver(token)
        claims = jwt.decode(
            token,
            clave,
            algorithms=["RS256"],
            audience=config["audience"],
            issuer=config["issuer"],
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except ExpiredSignatureError as error:
        raise AuthError(401, "El token expiró.") from error
    except InvalidAudienceError as error:
        raise AuthError(401, "La audiencia del token no es raapi.") from error
    except InvalidIssuerError as error:
        raise AuthError(401, "El emisor del token no es válido.") from error
    except PyJWTError as error:
        raise AuthError(401, "El token no es válido.") from error

    roles = (
        (claims.get("resource_access") or {})
        .get(config["audience"], {})
        .get("roles")
        or []
    )
    if not isinstance(roles, list):
        roles = []
    return {
        "sub": claims.get("sub"),
        "preferred_username": claims.get("preferred_username"),
        "email": claims.get("email"),
        "roles": set(roles),
        "claims": claims,
    }


def _bearer() -> str:
    header = request.headers.get("Authorization", "")
    esquema, _, token = header.partition(" ")
    if esquema.lower() != "bearer" or not token.strip():
        raise AuthError(401, "Se requiere un token Bearer.")
    return token.strip()


def _es_publica() -> bool:
    if request.method == "OPTIONS":
        return True
    path = request.path or ""
    if path in RUTAS_PUBLICAS or path.startswith(PREFIJOS_PUBLICOS):
        return True
    return False


def instalar_autenticacion(app, *, decoder=None) -> None:
    decodificar = decoder or decodificar_token

    @app.before_request
    def proteger():
        if _es_publica():
            return None
        try:
            identidad = decodificar(_bearer())
        except AuthError as error:
            if error.status >= 500:
                return jsonify({"error": error.message}), error.status
            return jsonify({"error": error.message}), error.status
        g.identidad = identidad
        rol = ROLES_POR_ENDPOINT.get(request.endpoint or "")
        if rol and rol not in identidad["roles"]:
            return jsonify({"error": "No tiene permiso para esta operación."}), 403
        return None


def identidad_actual() -> dict | None:
    return getattr(g, "identidad", None)
