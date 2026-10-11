from ra_mcp.service import agregar_pedido

from fakes import client_con, sin_conexion


def _api_ok():
    return client_con(
        lambda method, url, body: (200, {"mensaje": "Cliente actualizado correctamente."})
    )


def test_agregar_pedido_correctamente():
    api, transport = _api_ok()

    resultado = agregar_pedido(145, 2, 3, api)

    assert resultado == {
        "success": True,
        "id_cliente": 145,
        "cantidad_docenas": 2,
        "nro_pao": 3,
        "tiene_pedido": 1,
        "mensaje": "Cliente actualizado correctamente.",
    }
    assert transport.calls == [
        {
            "method": "PUT",
            "url": "http://raapi.test/api/clientes/actualizar/145",
            "body": {"docenas": 2, "nro_pao": 3, "tiene_pedido": True},
            "timeout": 30.0,
        }
    ]


def test_media_docena_se_envia_como_cantidad():
    api, transport = _api_ok()

    resultado = agregar_pedido(145, 1.5, 3, api)

    assert resultado["success"] is True
    assert resultado["cantidad_docenas"] == 1.5
    assert transport.calls[0]["body"]["docenas"] == 1.5


def test_cliente_inexistente():
    api, transport = client_con(
        lambda method, url, body: (404, {"error": "Cliente con ID 999 no encontrado."})
    )

    resultado = agregar_pedido(999, 2, 3, api)

    assert resultado["success"] is False
    assert resultado["error_code"] == "CLIENT_NOT_FOUND"
    assert resultado["message"] == "No existe el cliente indicado."
    assert resultado["id_cliente"] == 999
    assert resultado["detalle"] == "Cliente con ID 999 no encontrado."
    assert len(transport.calls) == 1


def test_cantidad_cero_no_llama_a_raapi():
    api, transport = _api_ok()

    resultado = agregar_pedido(145, 0, 3, api)

    assert resultado == {
        "success": False,
        "error_code": "INVALID_CANTIDAD",
        "message": "La cantidad de docenas debe ser un número mayor que cero.",
    }
    assert transport.calls == []


def test_cantidad_negativa_no_llama_a_raapi():
    api, transport = _api_ok()

    resultado = agregar_pedido(145, -2, 3, api)

    assert resultado["success"] is False
    assert resultado["error_code"] == "INVALID_CANTIDAD"
    assert transport.calls == []


def test_nro_pao_invalido_no_llama_a_raapi():
    api, transport = _api_ok()

    for invalido in (0, -3, 2.5, True, None, "3", "abc"):
        resultado = agregar_pedido(145, 2, invalido, api)
        assert resultado["success"] is False
        assert resultado["error_code"] == "INVALID_NRO_PAO"

    assert transport.calls == []


def test_error_retornado_por_raapi():
    api, _transport = client_con(
        lambda method, url, body: (400, {"error": "No se proporcionaron campos válidos para actualizar."})
    )

    resultado = agregar_pedido(145, 2, 3, api)

    assert resultado["success"] is False
    assert resultado["error_code"] == "RAAPI_REJECTED"
    assert resultado["message"] == "No se proporcionaron campos válidos para actualizar."


def test_error_interno_de_raapi():
    api, _transport = client_con(
        lambda method, url, body: (500, {"error": "Error interno del servidor al actualizar el cliente."})
    )

    resultado = agregar_pedido(145, 2, 3, api)

    assert resultado["success"] is False
    assert resultado["error_code"] == "RAAPI_ERROR"
    assert "success" in resultado and resultado["success"] is not True


def test_error_de_comunicacion_al_agregar():
    api, transport = client_con(sin_conexion)

    resultado = agregar_pedido(145, 2, 3, api)

    assert resultado["success"] is False
    assert resultado["error_code"] == "RAAPI_UNAVAILABLE"
    assert transport.calls[0]["method"] == "PUT"


def test_id_cliente_invalido_no_llama_a_raapi():
    api, transport = _api_ok()

    for invalido in (0, -1, True, 1.5, "145"):
        resultado = agregar_pedido(invalido, 2, 3, api)
        assert resultado["success"] is False
        assert resultado["error_code"] == "INVALID_ID_CLIENTE"

    assert transport.calls == []
