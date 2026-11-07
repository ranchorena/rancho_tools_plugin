"""Deja sin pedido activo a los clientes. No borra filas de la tabla pedido."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.infrastructure.unit_of_work import UnitOfWork


def iniciar_pedidos(uow: UnitOfWork) -> dict:
    def operacion() -> dict:
        actualizados = uow.clientes.iniciar_pedidos()
        if actualizados:
            return {"mensaje": f"Se iniciaron los pedidos. {actualizados} clientes quedaron sin pedido activo."}
        return {"mensaje": "No había clientes con pedido activo."}

    return ejecutar(uow, operacion, "Error interno del servidor al iniciar los pedidos.")
