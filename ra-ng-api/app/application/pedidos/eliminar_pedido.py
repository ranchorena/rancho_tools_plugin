"""Elimina un pedido. La marca del cliente se conserva si queda otro pedido de hoy o posterior."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.infrastructure.unit_of_work import UnitOfWork


def eliminar_pedido(uow: UnitOfWork, datos: dict) -> dict:
    id_pedido = datos.get("id_pedido") if datos else None
    if not isinstance(id_pedido, int) or isinstance(id_pedido, bool) or id_pedido <= 0:
        raise DomainError(400, "Indicá el id_pedido a eliminar.")

    def operacion() -> dict:
        pedido = uow.pedidos.obtener(id_pedido)
        if pedido is None:
            raise DomainError(404, "Pedido no encontrado.")
        id_cliente = pedido.id_cliente
        conserva = False
        if id_cliente is not None:
            conserva = uow.pedidos.conserva_otro_vigente(id_cliente, id_pedido)
        uow.pedidos.eliminar(pedido)
        if id_cliente is not None and not conserva:
            uow.clientes.quitar_marca_pedido(id_cliente)
        return {"mensaje": "Pedido eliminado correctamente."}

    return ejecutar(uow, operacion, "Error interno del servidor al eliminar el pedido.")
