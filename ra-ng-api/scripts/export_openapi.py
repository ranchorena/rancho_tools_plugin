"""Escribe openapi.yaml desde la aplicación. No abre la base."""

from pathlib import Path

import yaml

from app.main import app

destino = Path(__file__).resolve().parents[1] / "openapi.yaml"
destino.write_text(
    yaml.safe_dump(app.openapi(), sort_keys=False, allow_unicode=True),
    encoding="utf-8",
)
print(destino)
