"""Expresión SQL que iguala el plegado de app.domain.texto.plegar."""

from __future__ import annotations

from sqlalchemy import func

_DESDE = "ÁÉÍÓÚÜÑáéíóúüñ"
_HACIA = "aeiouunaeiouun"


def columna_plegada(columna):
    return func.translate(func.lower(func.coalesce(columna, "")), _DESDE, _HACIA)


def sql_plegado(columna: str) -> str:
    if not columna.isidentifier():
        raise ValueError(columna)
    return (
        f"translate(lower(coalesce({columna}, '')), "
        f"'{_DESDE}', '{_HACIA}')"
    )
