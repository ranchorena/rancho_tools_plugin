"""Pedidos entre dos fechas. Sin fechas, usa el día del último pedido.

completo=true devuelve el tramo desde el primer pedido hasta el último y no
cambia el caso sin fechas.
"""

from __future__ import annotations

from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.domain.pedidos.fechas import parse_fecha_query
from app.infrastructure.unit_of_work import UnitOfWork


def listar_historico(
    uow: UnitOfWork,
    desde_texto: str | None,
    hasta_texto: str | None,
    completo: bool = False,
) -> dict:
    if completo:
        desde = hasta = None
    else:
        try:
            desde = parse_fecha_query(desde_texto, "desde")
            hasta = parse_fecha_query(hasta_texto, "hasta")
        except ValueError as error:
            raise DomainError(400, str(error)) from error

    def operacion() -> dict:
        if completo:
            inicio = uow.pedidos.primera_fecha()
            fin = uow.pedidos.ultima_fecha()
            if inicio is None or fin is None:
                return {"fecha_desde": None, "fecha_hasta": None, "pedidos": []}
            return {
                "fecha_desde": inicio.isoformat(),
                "fecha_hasta": fin.isoformat(),
                "pedidos": uow.pedidos.historico(inicio, fin),
            }
        inicio, fin = desde, hasta
        if inicio is None and fin is None:
            ultima = uow.pedidos.ultima_fecha()
            if ultima is None:
                return {"fecha_desde": None, "fecha_hasta": None, "pedidos": []}
            inicio = fin = ultima
        elif inicio is None or fin is None:
            raise DomainError(400, "Indicá la fecha desde y la fecha hasta.")
        if inicio > fin:
            raise DomainError(400, "La fecha desde no puede ser posterior a la fecha hasta.")
        return {
            "fecha_desde": inicio.isoformat(),
            "fecha_hasta": fin.isoformat(),
            "pedidos": uow.pedidos.historico(inicio, fin),
        }

    return ejecutar(uow, operacion, "Error interno del servidor al obtener el historial de pedidos.")
