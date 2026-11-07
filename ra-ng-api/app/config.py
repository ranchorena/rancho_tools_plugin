"""Configuración leída del entorno del proceso. No usa archivo .env."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import quote_plus


def _schema(valor: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", valor):
        raise RuntimeError("DB_SCHEMA no es un identificador válido.")
    return valor


@dataclass(frozen=True)
class Settings:
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    db_schema: str
    database_url: str
    keycloak_issuer: str
    keycloak_jwks_url: str
    audience: str
    cors_origins: list[str]

    @classmethod
    def from_environ(cls) -> Settings:
        usuario = os.environ.get("DB_USER", "postgres")
        clave = os.environ.get("DB_PASSWORD", "postgres")
        host = os.environ.get("DB_HOST", "localhost")
        # Un proceso fuera del contenedor no resuelve el hostname db.
        if host == "db" and not os.path.exists("/app"):
            host = "localhost"
        puerto = os.environ.get("DB_PORT", "5432")
        nombre = os.environ.get("DB_NAME", "postgres")
        schema = _schema(os.environ.get("DB_SCHEMA", "generalbelgrano"))
        url = (
            f"postgresql+psycopg://{quote_plus(usuario)}:{quote_plus(clave)}"
            f"@{host}:{puerto}/{quote_plus(nombre)}"
        )
        origenes = [
            origen.strip()
            for origen in os.environ.get("CORS_ORIGINS", "http://localhost:8080").split(",")
            if origen.strip()
        ]
        return cls(
            db_user=usuario,
            db_password=clave,
            db_host=host,
            db_port=puerto,
            db_name=nombre,
            db_schema=schema,
            database_url=url,
            keycloak_issuer=os.environ.get("KEYCLOAK_ISSUER", "").strip(),
            keycloak_jwks_url=os.environ.get("KEYCLOAK_JWKS_URL", "").strip(),
            audience=os.environ.get("RA_API_AUDIENCE", "raapi").strip() or "raapi",
            cors_origins=origenes,
        )


settings = Settings.from_environ()
