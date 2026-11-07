"""Clientes con pedido activo y geometría. Vacío no es una lista."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.infrastructure.unit_of_work import UnitOfWork


def listar_clientes_con_pedido(uow: UnitOfWork):
    def operacion():
        clientes = uow.clientes.listar_con_pedido()
        if not clientes:
            return {"message": "No se encontraron clientes con pedidos"}
        return clientes

    return ejecutar(uow, operacion, "Error interno del servidor al obtener clientes con pedidos.")
