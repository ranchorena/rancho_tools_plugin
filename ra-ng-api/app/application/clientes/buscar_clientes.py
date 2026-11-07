"""Búsqueda de clientes por nombre, dirección o calle y altura."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.infrastructure.unit_of_work import UnitOfWork


def buscar_clientes(uow: UnitOfWork, datos: dict) -> list[dict]:
    def operacion() -> list[dict]:
        if not datos or "criterio" not in datos:
            raise DomainError(400, "El campo 'criterio' es requerido")
        criterio = datos.get("criterio")
        if criterio == "nombre":
            nombre = datos.get("nombre_cliente")
            if not nombre:
                raise DomainError(400, "El campo 'nombre_cliente' es requerido para el criterio 'nombre'")
            return uow.clientes.buscar_por_nombre(nombre)
        if criterio == "direccion":
            direccion = datos.get("direccion")
            if not direccion:
                raise DomainError(400, "El campo 'direccion' es requerido para el criterio 'direccion'")
            return uow.clientes.buscar_por_direccion(direccion)
        if criterio == "calle_altura":
            calle = datos.get("calle")
            if not calle:
                raise DomainError(400, "El campo 'calle' es requerido para el criterio 'calle_altura'")
            return uow.clientes.buscar_por_calle_altura(calle, datos.get("altura"))
        raise DomainError(
            400,
            f"Criterio '{criterio}' no válido. Use 'nombre', 'direccion' o 'calle_altura'.",
        )

    return ejecutar(uow, operacion, "Error interno del servidor al buscar clientes.")
