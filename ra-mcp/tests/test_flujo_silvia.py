"""Escenario: Agregar un pedido al cliente Silvia, 2 docenas nro_pao 3.

Si hay varias Silvias, ninguna se modifica hasta que se elige un id_cliente.
"""

from ra_mcp.service import MULTIPLE_MATCHES, agregar_pedido, buscar_cliente

from fakes import client_con, cliente

SILVIAS = [
    cliente(145, "Silvia Gómez", "San Martín 100", "San Martín", 100),
    cliente(327, "Silvia Pérez", "Belgrano 200", "Belgrano", 200),
    cliente(401, "Silvia Rodríguez", "Mitre 300", "Mitre", 300),
]


def _raapi_silvia():
    def responder(method, url, body):
        if method == "POST" and url.endswith("/api/clientes/buscar"):
            assert body == {"criterio": "nombre", "nombre_cliente": "Silvia"}
            return 200, SILVIAS
        if method == "PUT" and url.endswith("/api/clientes/actualizar/145"):
            assert body == {"docenas": 2, "nro_pao": 3, "tiene_pedido": True}
            return 200, {"mensaje": "Cliente actualizado correctamente."}
        raise AssertionError(f"Llamada inesperada: {method} {url} {body}")

    return client_con(responder)


def test_varias_silvias_no_registran_pedido_hasta_la_seleccion():
    api, transport = _raapi_silvia()

    busqueda = buscar_cliente("Silvia", api)

    assert busqueda["status"] == MULTIPLE_MATCHES
    assert [item["nombre"] for item in busqueda["clientes"]] == [
        "Silvia Gómez",
        "Silvia Pérez",
        "Silvia Rodríguez",
    ]
    assert [call["method"] for call in transport.calls] == ["POST"]

    pedido = agregar_pedido(145, 2, 3, api)

    assert pedido["success"] is True
    assert pedido["id_cliente"] == 145
    assert pedido["cantidad_docenas"] == 2
    assert pedido["nro_pao"] == 3
    assert pedido["tiene_pedido"] == 1
    assert [call["method"] for call in transport.calls] == ["POST", "PUT"]
    assert transport.calls[1]["url"].endswith("/api/clientes/actualizar/145")


def test_una_sola_marta_puede_registrar_el_pedido():
    def responder(method, url, body):
        if method == "POST":
            return 200, [cliente(220, "Marta López", "Sarmiento 550", "Sarmiento", 550)]
        if method == "PUT":
            return 200, {"mensaje": "Cliente actualizado correctamente."}
        raise AssertionError(method)

    api, transport = client_con(responder)
    busqueda = buscar_cliente("Marta", api)
    assert busqueda["status"] == "ONE_MATCH"

    pedido = agregar_pedido(busqueda["id_cliente"], 1, 5, api)

    assert pedido["success"] is True
    assert pedido["id_cliente"] == 220
    assert transport.calls[1]["body"] == {"docenas": 1, "nro_pao": 5, "tiene_pedido": True}
