"""Misma serialización JSON que raapi: horas HH:MM:SS, fechas ISO y Decimal como float."""

from __future__ import annotations

import datetime
from decimal import Decimal


def valor_json(valor):
    if isinstance(valor, datetime.time):
        return valor.strftime("%H:%M:%S") if valor else None
    if isinstance(valor, datetime.datetime):
        return valor.isoformat() if valor else None
    if isinstance(valor, datetime.date):
        return valor.isoformat() if valor else None
    if isinstance(valor, Decimal):
        return float(valor) if valor is not None else None
    return valor


def fila_a_dict(fila) -> dict | None:
    if fila is None:
        return None
    if hasattr(fila, "_mapping"):
        datos = dict(fila._mapping)
    else:
        datos = dict(fila)
    return {clave: valor_json(valor) for clave, valor in datos.items()}
