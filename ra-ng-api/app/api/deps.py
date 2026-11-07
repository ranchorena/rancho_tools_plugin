"""Sesión por pedido HTTP y control de roles de raapi."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Depends, Request

from app.domain.errors import DomainError
from app.infrastructure.db import SessionFactory
from app.infrastructure.unit_of_work import UnitOfWork


def get_uow() -> Iterator[UnitOfWork]:
    session = SessionFactory()
    uow = UnitOfWork(session)
    try:
        yield uow
    except Exception:
        if not uow.committed:
            uow.rollback()
        raise
    else:
        if not uow.committed:
            uow.rollback()
    finally:
        session.close()


def exige_rol(rol: str):
    def _dependencia(request: Request) -> dict:
        identidad = getattr(request.state, "identidad", None)
        if identidad is None or rol not in identidad["roles"]:
            raise DomainError(403, "No tiene permiso para esta operación.")
        return identidad

    return _dependencia


def identidad_actual(request: Request) -> dict:
    return getattr(request.state, "identidad", None) or {}


RolLectura = Depends(exige_rol("clientes:read"))
RolEscritura = Depends(exige_rol("pedidos:write"))
UowDep = Depends(get_uow)
