from ra_mcp.service import ERROR, MULTIPLE_MATCHES, NO_MATCH, ONE_MATCH, buscar_cliente

from fakes import client_con, cliente, sin_conexion


def test_sin_coincidencias():
    api, transport = client_con(lambda method, url, body: (200, []))

    resultado = buscar_cliente("Silvia", api)

    assert resultado["status"] == NO_MATCH
    assert resultado["success"] is True
    assert resultado["clientes"] == []
    assert transport.calls[0]["method"] == "POST"
    assert transport.calls[0]["url"] == "http://raapi.test/api/clientes/buscar"
    assert transport.calls[0]["body"] == {"criterio": "nombre", "nombre_cliente": "Silvia"}
    assert all(call["method"] != "PUT" for call in transport.calls)


def test_una_coincidencia():
    fila = cliente(220, "Marta López", "San Martín 1250", "San Martín", 1250)
    api, _transport = client_con(lambda method, url, body: (200, [fila]))

    resultado = buscar_cliente("Marta", api)

    assert resultado["status"] == ONE_MATCH
    assert resultado["id_cliente"] == 220
    assert resultado["clientes"] == [
        {
            "id_cliente": 220,
            "nombre": "Marta López",
            "direccion": "San Martín 1250",
            "calle": "San Martín",
            "altura": 1250,
            "longitud": -58.4,
            "latitud": -34.6,
        }
    ]


def test_multiples_coincidencias_no_elige_cliente():
    filas = [
        cliente(145, "Silvia Gómez", "San Martín 100", "San Martín", 100),
        cliente(327, "Silvia Pérez", "Belgrano 200", "Belgrano", 200),
        cliente(401, "Silvia Rodríguez", "Mitre 300", "Mitre", 300),
    ]
    api, transport = client_con(lambda method, url, body: (200, filas))

    resultado = buscar_cliente("Silvia", api)

    assert resultado["status"] == MULTIPLE_MATCHES
    assert resultado["requiere_seleccion"] is True
    assert [item["id_cliente"] for item in resultado["clientes"]] == [145, 327, 401]
    assert "id_cliente" not in resultado
    assert all(call["method"] != "PUT" for call in transport.calls)


def test_error_de_comunicacion():
    api, transport = client_con(sin_conexion)

    resultado = buscar_cliente("Silvia", api)

    assert resultado["status"] == ERROR
    assert resultado["success"] is False
    assert resultado["error_code"] == "RAAPI_UNAVAILABLE"
    assert resultado["clientes"] == []
    assert transport.calls[0]["method"] == "POST"


def test_error_http_de_raapi_no_es_ausencia_de_clientes():
    api, _transport = client_con(
        lambda method, url, body: (500, {"error": "Error interno del servidor al buscar clientes."})
    )

    resultado = buscar_cliente("Silvia", api)

    assert resultado["status"] == ERROR
    assert resultado["success"] is False
    assert resultado["error_code"] == "RAAPI_ERROR"
    assert resultado["status"] != NO_MATCH


def test_nombre_vacio_no_llama_a_raapi():
    api, transport = client_con(lambda method, url, body: (200, []))

    resultado = buscar_cliente("   ", api)

    assert resultado["error_code"] == "INVALID_NOMBRE"
    assert transport.calls == []


def test_respuesta_que_no_es_lista():
    api, _transport = client_con(lambda method, url, body: (200, {"message": "inesperado"}))

    resultado = buscar_cliente("Silvia", api)

    assert resultado["status"] == ERROR
    assert resultado["error_code"] == "RAAPI_ERROR"
