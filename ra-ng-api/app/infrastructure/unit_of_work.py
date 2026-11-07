"""Unit of Work sobre una Session de SQLAlchemy. El caso de uso confirma la transacción."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.infrastructure.persistence.callejero_repository import CallejeroRepository
from app.infrastructure.persistence.cliente_repository import ClienteRepository
from app.infrastructure.persistence.pedido_repository import PedidoRepository
from app.infrastructure.persistence.precio_repository import PrecioRepository


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.clientes = ClienteRepository(session)
        self.pedidos = PedidoRepository(session)
        self.precios = PrecioRepository(session)
        self.callejero = CallejeroRepository(session)
        self.committed = False

    def commit(self) -> None:
        self.session.commit()
        self.committed = True

    def rollback(self) -> None:
        self.session.rollback()
