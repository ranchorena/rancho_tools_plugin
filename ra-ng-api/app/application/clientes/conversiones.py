"""Conversiones de los DTO de cliente hacia los tipos de PostgreSQL."""

from __future__ import annotations

import datetime


def como_horario(valor):
    if isinstance(valor, datetime.time):
        return valor
    if not valor:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    if len(texto) == 5:
        texto += ":00"
    return datetime.time.fromisoformat(texto)
