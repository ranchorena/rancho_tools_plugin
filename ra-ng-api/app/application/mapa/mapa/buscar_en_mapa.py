"""Búsqueda de pedidos activos y clientes para la caja del mapa."""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.domain.texto import patron_contiene
from app.infrastructure.unit_of_work import UnitOfWork

_MINIMO = 3


def buscar_en_mapa(uow: UnitOfWork, texto: str) -> dict:
    def operacion() -> dict:
        consulta = (texto or "").strip()
        if len(consulta) < _MINIMO:
            raise DomainError(400, "Ingresá al menos 3 caracteres.")
        patron = patron_contiene(consulta)
        return {
            "pedidos": uow.pedidos.buscar_en_mapa(patron),
            "clientes": uow.clientes.buscar_en_mapa(patron),
        }

    return ejecutar(uow, operacion, "Error interno del servidor al buscar en el mapa.")
