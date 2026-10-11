"""Demostración reproducible del pedido a Silvia, sin base de datos.

Uso, desde ra-mcp:

    python scripts/flujo_silvia.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")

from ra_mcp.client import RaApiClient  # noqa: E402
from ra_mcp.service import agregar_pedido, buscar_cliente  # noqa: E402

SILVIAS = [
    {
        "id": 145,
        "nombre": "Silvia Gómez",
        "direccion": "San Martín 100",
        "calle": "San Martín",
        "altura": 100,
        "longitud": -58.41,
        "latitud": -34.61,
    },
    {
        "id": 327,
        "nombre": "Silvia Pérez",
        "direccion": "Belgrano 200",
        "calle": "Belgrano",
        "altura": 200,
        "longitud": -58.42,
        "latitud": -34.62,
    },
    {
        "id": 401,
        "nombre": "Silvia Rodríguez",
        "direccion": "Mitre 300",
        "calle": "Mitre",
        "altura": 300,
        "longitud": -58.43,
        "latitud": -34.63,
    },
]


def main() -> None:
    llamadas: list[dict] = []

    def transport(method, url, body, timeout):
        llamadas.append({"method": method, "url": url, "body": body})
        if method == "POST":
            return 200, SILVIAS
        if method == "PUT":
            return 200, {"mensaje": "Cliente actualizado correctamente."}
        raise AssertionError(method)

    client = RaApiClient("http://raapi.test", transport=transport)

    print("Prompt: Agregar un pedido al cliente Silvia, 2 docenas nro_pao 3")
    print("Extracción: nombre=Silvia, cantidad_docenas=2, nro_pao=3")
    busqueda = buscar_cliente("Silvia", client)
    print("buscar_cliente:")
    print(json.dumps(busqueda, ensure_ascii=False, indent=2))

    if busqueda["status"] != "MULTIPLE_MATCHES":
        raise SystemExit("Se esperaban varias Silvias y el flujo no debía registrar el pedido.")
    if any(item["method"] == "PUT" for item in llamadas):
        raise SystemExit("Se modificó un cliente antes de resolver la ambigüedad.")

    print()
    print("Hay varias coincidencias. No se registra el pedido.")
    for indice, item in enumerate(busqueda["clientes"], start=1):
        print(
            f"{indice}. {item['nombre']} — Cliente {item['id_cliente']} — {item['direccion']}"
        )
    print("¿Cuál querés usar?")
    print()
    print("Selección del usuario: id_cliente=145")
    pedido = agregar_pedido(145, 2, 3, client)
    print("agregar_pedido:")
    print(json.dumps(pedido, ensure_ascii=False, indent=2))
    print("Llamadas a raapi:")
    print(json.dumps(llamadas, ensure_ascii=False, indent=2))

    if llamadas[-1] != {
        "method": "PUT",
        "url": "http://raapi.test/api/clientes/actualizar/145",
        "body": {"docenas": 2, "nro_pao": 3, "tiene_pedido": True},
    }:
        raise SystemExit("El pedido no se registró sobre el id seleccionado.")
    if pedido.get("success") is not True:
        raise SystemExit("raapi no confirmó el pedido.")
    if any(item["method"] == "PUT" and not item["url"].endswith("/145") for item in llamadas):
        raise SystemExit("Se actualizó un cliente distinto del seleccionado.")


if __name__ == "__main__":
    main()
