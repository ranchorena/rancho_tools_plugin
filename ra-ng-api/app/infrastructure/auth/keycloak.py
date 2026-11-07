"""Resource server de Keycloak. La audiencia sigue siendo raapi para los tokens de raweb."""

from __future__ import annotations

from functools import lru_cache

import jwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError, PyJWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.domain.errors import DomainError

RUTAS_PUBLICAS = {"/", "/health", "/openapi.json", "/favicon.ico"}
PREFIJOS_PUBLICOS = ("/docs", "/redoc")


class AuthError(DomainError):
    pass


def _configuracion() -> dict:
    if not settings.keycloak_issuer or not settings.keycloak_jwks_url:
        raise AuthError(500, "La validación de tokens no está configurada.")
    return {
        "issuer": settings.keycloak_issuer,
        "jwks_url": settings.keycloak_jwks_url,
        "audience": settings.audience,
    }


@lru_cache(maxsize=4)
def _cliente_jwks(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=300)


def decodificar_token(token: str) -> dict:
    config = _configuracion()
    try:
        clave = _cliente_jwks(config["jwks_url"]).get_signing_key_from_jwt(token).key
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

    roles = ((claims.get("resource_access") or {}).get(config["audience"], {}) or {}).get("roles") or []
    if not isinstance(roles, list):
        roles = []
    return {
        "sub": claims.get("sub"),
        "preferred_username": claims.get("preferred_username"),
        "email": claims.get("email"),
        "roles": set(roles),
        "claims": claims,
    }


def _es_publica(request: Request) -> bool:
    if request.method == "OPTIONS":
        return True
    path = request.url.path or ""
    return path in RUTAS_PUBLICAS or path.startswith(PREFIJOS_PUBLICOS)


class AutenticacionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if _es_publica(request):
            return await call_next(request)
        header = request.headers.get("authorization", "")
        esquema, _, token = header.partition(" ")
        if esquema.lower() != "bearer" or not token.strip():
            return JSONResponse({"error": "Se requiere un token Bearer."}, status_code=401)
        try:
            request.state.identidad = decodificar_token(token.strip())
        except AuthError as error:
            return JSONResponse({"error": error.message}, status_code=error.status)
        return await call_next(request)
