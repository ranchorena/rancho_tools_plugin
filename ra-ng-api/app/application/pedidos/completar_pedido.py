"""Marca un pedido como completado o pendiente."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.infrastructure.unit_of_work import UnitOfWork


def completar_pedido(uow: UnitOfWork, datos: dict) -> dict:
    id_pedido = datos.get("id_pedido") if datos else None
    completado = datos.get("completado") if datos else None
    if not isinstance(id_pedido, int) or isinstance(id_pedido, bool) or id_pedido <= 0:
        raise DomainError(400, "Indicá el id_pedido y si el pedido está completado.")
    if completado is True:
        completado = 1
    elif completado is False:
        completado = 0
    if completado not in (0, 1):
        raise DomainError(400, "Indicá el id_pedido y si el pedido está completado.")

    def operacion() -> dict:
        pedido = uow.pedidos.obtener(id_pedido)
        if pedido is None:
            raise DomainError(404, "Pedido no encontrado.")
        pedido.completado = completado
        if completado == 1:
            return {"mensaje": "Pedido marcado como completado."}
        return {"mensaje": "Pedido marcado como pendiente."}

    return ejecutar(uow, operacion, "Error interno del servidor al actualizar el pedido.")
