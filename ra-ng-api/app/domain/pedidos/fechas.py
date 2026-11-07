"""Fechas de pedido: si no viene fecha, el pedido queda para mañana."""

from __future__ import annotations

import datetime


def fecha_pedido(datos: dict) -> datetime.date | None:
    if "fecha" not in datos or datos.get("fecha") in (None, ""):
        return datetime.date.today() + datetime.timedelta(days=1)

    valor = datos.get("fecha")
    if isinstance(valor, datetime.datetime):
        return valor.date()
    if isinstance(valor, datetime.date):
        return valor
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return datetime.date.today() + datetime.timedelta(days=1)
        try:
            return datetime.date.fromisoformat(texto[:10])
        except ValueError:
            return None
    return None


def parse_fecha_query(valor: str | None, nombre: str) -> datetime.date | None:
    if valor is None or valor.strip() == "":
        return None
    try:
        return datetime.datetime.strptime(valor.strip()[:10], "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError(f"La fecha {nombre} no es válida.") from error
