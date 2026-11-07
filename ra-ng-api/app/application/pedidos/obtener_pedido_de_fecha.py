"""Pedido de un cliente para un día. Sin pedido, el cuerpo trae pedido null."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.domain.pedidos.fechas import parse_fecha_query
from app.infrastructure.unit_of_work import UnitOfWork


def obtener_pedido_de_fecha(uow: UnitOfWork, cliente_id: int, fecha_texto: str | None) -> dict:
    try:
        if fecha_texto is None or fecha_texto.strip() == "":
            raise DomainError(400, "La fecha del pedido es requerida.")
        fecha = parse_fecha_query(fecha_texto, "del pedido")
    except DomainError:
        raise
    except ValueError as error:
        # parse_fecha_query dice "La fecha del pedido no es válida." si el nombre es "del pedido"? 
        # Original: "La fecha del pedido no es válida."
        raise DomainError(400, "La fecha del pedido no es válida.") from error

    def operacion() -> dict:
        if fecha is None:
            raise DomainError(400, "La fecha del pedido es requerida.")
        if not uow.clientes.existe(cliente_id):
            raise DomainError(404, f"Cliente con ID {cliente_id} no encontrado.")
        return {"pedido": uow.pedidos.de_fecha(cliente_id, fecha)}

    return ejecutar(uow, operacion, "Error interno del servidor al obtener el pedido.")
