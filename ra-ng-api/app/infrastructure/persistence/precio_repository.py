"""Precio vigente: el registro de fecha más reciente."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.persistence.models import Precio


class PrecioRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def vigente(self) -> float | None:
        consulta = select(Precio.precio).order_by(Precio.fecha.desc(), Precio.id_precio.desc()).limit(1)
        fila = self._session.execute(consulta).first()
        if fila is None or fila[0] is None:
            return None
        return float(fila[0])
