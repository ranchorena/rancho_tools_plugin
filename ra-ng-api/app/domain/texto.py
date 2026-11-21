"""Plegado de texto para búsquedas que no distinguen mayúsculas ni acentos."""

from __future__ import annotations

_ACENTOS = "áéíóúüñ"
_SIN_ACENTOS = "aeiouun"
_TABLA = str.maketrans(_ACENTOS, _SIN_ACENTOS)


def plegar(texto: str) -> str:
    return texto.lower().translate(_TABLA)


def patron_contiene(texto: str) -> str:
    """Patrón LIKE ya plegado. % y _ del usuario no actúan como comodines."""
    escapado = (
        plegar(texto)
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escapado}%"
