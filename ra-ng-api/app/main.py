"""Punto de entrada de ra-ng-api."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.errores import instalar_manejadores
from app.api.v1.registrar import construir_router
from app.config import settings
from app.infrastructure.auth.keycloak import AutenticacionMiddleware

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="ra-ng-api",
    version="1.0.0",
    description=(
        "API de clientes, pedidos, direcciones y rutas del rancho. "
        "El contrato versionado está en /api/v1. Las mismas operaciones están en /api "
        "para que raweb siga usando las rutas actuales."
    ),
    openapi_version="3.1.0",
)
instalar_manejadores(app)
app.add_middleware(AutenticacionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
app.include_router(construir_router("v1"), prefix="/api/v1")
app.include_router(construir_router("compat"), prefix="/api")


@app.get("/", include_in_schema=False)
def raiz():
    return HTMLResponse("<h1>Server is running</h1>")


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
