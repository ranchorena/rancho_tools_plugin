from ra_mcp.service import pedidos_historico

from fakes import client_con, sin_conexion


def _pedido(id_pedido, cantidad, precio, es_regalo=0, nombre="Silvia"):
    return {
        "id": id_pedido,
        "id_cliente": 2,
        "nombre": nombre,
        "direccion": "Guemes 1068",
        "cantidad": cantidad,
        "telefono": None,
        "horario": None,
        "nro_pao": None,
        "es_regalo": es_regalo,
        "precio_unitario": precio,
        "observacion": None,
        "longitud": -58.48,
        "latitud": -35.76,
    }


def _cuerpo(pedidos, desde="2026-10-11", hasta="2026-10-11"):
    return {
        "fecha_desde": desde,
        "fecha_hasta": hasta,
        "pedidos": pedidos,
    }


def test_sin_fechas_consulta_el_ultimo_dia_y_calcula_estadisticas():
    pedidos = [
        _pedido(1, 2.5, 5000),
        _pedido(2, 1, 5000, es_regalo=1, nombre="Marisa"),
    ]
    api, transport = client_con(lambda method, url, body: (200, _cuerpo(pedidos)))

    resultado = pedidos_historico(None, None, api)

    assert resultado["success"] is True
    assert resultado["fecha_desde"] == "2026-10-11"
    assert resultado["fecha_hasta"] == "2026-10-11"
    assert resultado["pedidos"] == pedidos
    assert resultado["estadisticas"] == {
        "cantidad_total": 3.5,
        "cantidad_vendida": 2.5,
        "valor_total": 12500.0,
    }
    assert transport.calls == [
        {
            "method": "GET",
            "url": "http://raapi.test/api/pedidos/historico",
            "body": None,
            "timeout": 30.0,
        }
    ]


def test_rango_de_fechas_se_envia_en_la_consulta():
    api, transport = client_con(
        lambda method, url, body: (200, _cuerpo([_pedido(3, 1, 4000)], "2026-10-01", "2026-10-11"))
    )

    resultado = pedidos_historico("2026-10-01", "2026-10-11", api)

    assert resultado["success"] is True
    assert resultado["estadisticas"]["valor_total"] == 4000.0
    assert transport.calls[0]["url"] == (
        "http://raapi.test/api/pedidos/historico?desde=2026-10-01&hasta=2026-10-11"
    )


def test_fechas_en_blanco_equivalen_a_no_enviarlas():
    api, transport = client_con(lambda method, url, body: (200, _cuerpo([] , None, None)))

    resultado = pedidos_historico("  ", "", api)

    assert resultado["success"] is True
    assert resultado["message"] == "No hay pedidos registrados."
    assert resultado["estadisticas"]["cantidad_total"] == 0
    assert transport.calls[0]["url"] == "http://raapi.test/api/pedidos/historico"


def test_periodo_sin_pedidos():
    api, _transport = client_con(
        lambda method, url, body: (200, _cuerpo([], "2026-01-01", "2026-01-02"))
    )

    resultado = pedidos_historico("2026-01-01", "2026-01-02", api)

    assert resultado["success"] is True
    assert resultado["pedidos"] == []
    assert resultado["message"] == "No se encontraron pedidos para las fechas indicadas."


def test_una_sola_fecha_no_llama_a_raapi():
    api, transport = client_con(lambda method, url, body: (200, _cuerpo([])))

    resultado = pedidos_historico("2026-10-11", None, api)

    assert resultado["success"] is False
    assert resultado["error_code"] == "INVALID_FECHA"
    assert resultado["message"] == "Indicá la fecha desde y la fecha hasta."
    assert transport.calls == []


def test_fecha_invalida_no_llama_a_raapi():
    api, transport = client_con(lambda method, url, body: (200, _cuerpo([])))

    resultado = pedidos_historico("11/10/2026", "2026-10-11", api)

    assert resultado["error_code"] == "INVALID_FECHA"
    assert transport.calls == []


def test_desde_posterior_a_hasta_no_llama_a_raapi():
    api, transport = client_con(lambda method, url, body: (200, _cuerpo([])))

    resultado = pedidos_historico("2026-10-12", "2026-10-11", api)

    assert resultado["error_code"] == "INVALID_FECHA"
    assert "posterior" in resultado["message"]
    assert transport.calls == []


def test_rechazo_de_raapi():
    api, _transport = client_con(
        lambda method, url, body: (400, {"error": "La fecha desde no es válida."})
    )

    resultado = pedidos_historico("2026-10-11", "2026-10-11", api)

    assert resultado["success"] is False
    assert resultado["error_code"] == "RAAPI_REJECTED"
    assert resultado["message"] == "La fecha desde no es válida."
    assert resultado["pedidos"] == []


def test_sin_conexion():
    api, _transport = client_con(sin_conexion)

    resultado = pedidos_historico(None, None, api)

    assert resultado["error_code"] == "RAAPI_UNAVAILABLE"
    assert resultado["estadisticas"]["valor_total"] == 0
