"""El sobre de error de raweb es {\"error\": ...}, también cuando falla la validación."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.domain.errors import DomainError


def _mensaje_validacion(request: Request, exc: RequestValidationError) -> str:
    path = request.url.path
    for error in exc.errors():
        loc = error.get("loc") or ()
        tipo = error.get("type") or ""
        campo = loc[-1] if loc else ""
        if "/clientes/agregar" in path and campo == "direccion" and "missing" in tipo:
            return "La dirección del cliente es requerida."
        if "/clientes/actualizar/" in path and campo == "body":
            return "No se proporcionaron datos para actualizar."
        if campo == "direccion" and "missing" in tipo:
            return "La dirección es requerida"
        if campo == "criterio" and "missing" in tipo:
            return "El campo 'criterio' es requerido"
        if campo == "nombre" and "missing" in tipo:
            return "El nombre del cliente es requerido."
        if campo == "direccion" and "missing" in tipo and path.endswith("/clientes/agregar"):
            return "La dirección del cliente es requerida."
        if campo in ("latitud", "longitud") and "missing" in tipo:
            return "Las coordenadas (latitud y longitud) son requeridas."
        if path.endswith("/pedidos/eliminar") and (campo == "id_pedido" or campo == "body"):
            return "Indicá el id_pedido a eliminar."
    if path.endswith("/pedidos/eliminar"):
        return "Indicá el id_pedido a eliminar."
    return "Los datos enviados no son válidos."


def instalar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def dominio(_request: Request, exc: DomainError):
        return JSONResponse({"error": exc.message}, status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def validacion(request: Request, exc: RequestValidationError):
        return JSONResponse({"error": _mensaje_validacion(request, exc)}, status_code=400)
