"""Cierra la transacción del caso de uso y unifica el error interno."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

from app.domain.errors import DomainError
from app.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger("ra_ng_api")
T = TypeVar("T")


def ejecutar(uow: UnitOfWork, operacion: Callable[[], T], mensaje_error: str) -> T:
    try:
        resultado = operacion()
        uow.commit()
        return resultado
    except DomainError:
        raise
    except Exception:
        logger.exception(mensaje_error)
        raise DomainError(500, mensaje_error) from None
