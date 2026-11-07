"""Separa 'Nombre de calle número' en calle y altura."""

from __future__ import annotations

import re


def parse_direccion(direccion: str) -> tuple[str | None, int | None]:
    coincidencia = re.match(r"^(.*?)\s*(\d+)\s*$", direccion.strip())
    if not coincidencia:
        return None, None
    calle = coincidencia.group(1).strip().upper()
    try:
        return calle, int(coincidencia.group(2))
    except ValueError:
        return None, None
