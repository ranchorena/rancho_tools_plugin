"""Reglas de orquestación del MCP.

La persistencia queda en raapi. Aquí solo se valida la entrada del tool,
se interpreta el contrato HTTP y se arma una respuesta estructurada.
"""

from __future__ import annotations

import math
import re
from datetime import date
from typing import Any

from ra_mcp.client import (
    RaApiClient,
    RaApiConnectionError,
    RaApiHttpError,
    RaApiResponseError,
    mensaje_de_cuerpo,
)

NO_MATCH = "NO_MATCH"
ONE_MATCH = "ONE_MATCH"
MULTIPLE_MATCHES = "MULTIPLE_MATCHES"
ERROR = "ERROR"

INVALID_NOMBRE = "INVALID_NOMBRE"
INVALID_ID_CLIENTE = "INVALID_ID_CLIENTE"
INVALID_CANTIDAD = "INVALID_CANTIDAD"
INVALID_NRO_PAO = "INVALID_NRO_PAO"
INVALID_FECHA = "INVALID_FECHA"
CLIENT_NOT_FOUND = "CLIENT_NOT_FOUND"
RAAPI_UNAVAILABLE = "RAAPI_UNAVAILABLE"
RAAPI_NOT_CONFIGURED = "RAAPI_NOT_CONFIGURED"
RAAPI_ERROR = "RAAPI_ERROR"
RAAPI_REJECTED = "RAAPI_REJECTED"

_CAMPOS_BUSQUEDA = ("nombre", "direccion", "calle", "altura", "longitud", "latitud")
_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ESTADISTICAS_VACIAS = {
    "cantidad_total": 0,
    "cantidad_vendida": 0,
    "valor_total": 0,
}


def buscar_cliente(nombre: str, client: RaApiClient) -> dict:
    """Busca por nombre y clasifica 0, 1 o varias coincidencias.

    No elige un cliente cuando hay más de uno y no llama a ningún endpoint
    de actualización.
    """
    consulta = nombre.strip() if isinstance(nombre, str) else ""
    if not consulta:
        return _error_busqueda(
            INVALID_NOMBRE,
            "El nombre del cliente es requerido.",
        )

    try:
        filas = client.buscar_por_nombre(consulta)
    except RaApiConnectionError as error:
        return _error_busqueda(RAAPI_UNAVAILABLE, error.message)
    except RaApiHttpError as error:
        return _error_busqueda(_codigo_http(error), _mensaje_http(error))
    except RaApiResponseError as error:
        return _error_busqueda(RAAPI_ERROR, error.message)

    try:
        clientes = [_cliente_busqueda(fila) for fila in filas]
    except ValueError as error:
        return _error_busqueda(RAAPI_ERROR, str(error))

    if not clientes:
        return {
            "status": NO_MATCH,
            "success": True,
            "clientes": [],
            "message": "No existe coincidencia para el nombre indicado.",
        }

    if len(clientes) == 1:
        return {
            "status": ONE_MATCH,
            "success": True,
            "id_cliente": clientes[0]["id_cliente"],
            "clientes": clientes,
            "message": "Se encontró un único cliente. Las operaciones siguientes deben usar su id_cliente.",
        }

    return {
        "status": MULTIPLE_MATCHES,
        "success": True,
        "requiere_seleccion": True,
        "clientes": clientes,
        "message": (
            "Hay varias coincidencias. Pedí al usuario que elija un id_cliente "
            "antes de registrar un pedido. No elijas automáticamente."
        ),
    }


def agregar_pedido(
    id_cliente: Any,
    cantidad_docenas: Any,
    nro_pao: Any,
    client: RaApiClient,
) -> dict:
    """Registra el pedido del cliente ya identificado.

    Si la validación local falla, no se llama a raapi. Si raapi rechaza la
    operación, la respuesta queda en success false.
    """
    if not _es_entero_positivo(id_cliente):
        return _error_pedido(
            INVALID_ID_CLIENTE,
            "id_cliente debe ser un entero positivo.",
        )
    if not _es_cantidad_valida(cantidad_docenas):
        return _error_pedido(
            INVALID_CANTIDAD,
            "La cantidad de docenas debe ser un número mayor que cero.",
        )
    if not _es_entero_positivo(nro_pao):
        return _error_pedido(
            INVALID_NRO_PAO,
            "nro_pao debe ser un entero positivo.",
        )

    try:
        body = client.registrar_pedido(id_cliente, cantidad_docenas, nro_pao)
    except RaApiConnectionError as error:
        return _error_pedido(RAAPI_UNAVAILABLE, error.message, id_cliente=id_cliente)
    except RaApiHttpError as error:
        return _error_pedido(
            _codigo_http(error),
            _mensaje_pedido_http(error),
            id_cliente=id_cliente,
            detalle=mensaje_de_cuerpo(error.body),
        )
    except RaApiResponseError as error:
        return _error_pedido(RAAPI_ERROR, error.message, id_cliente=id_cliente)

    return {
        "success": True,
        "id_cliente": id_cliente,
        "cantidad_docenas": cantidad_docenas,
        "nro_pao": nro_pao,
        "tiene_pedido": 1,
        "mensaje": body["mensaje"],
    }


def pedidos_historico(
    desde: str | None,
    hasta: str | None,
    client: RaApiClient,
) -> dict:
    """Lista los pedidos del período y calcula las mismas estadísticas del formulario.

    Sin fechas, no arma consulta: raapi responde el día del pedido más reciente.
    Los regalos entran en la cantidad total y quedan fuera de la cantidad vendida
    y del valor.
    """
    try:
        fecha_desde, fecha_hasta = _rango_fechas(desde, hasta)
    except ValueError as error:
        return _error_historico(INVALID_FECHA, str(error))

    try:
        body = client.pedidos_historico(fecha_desde, fecha_hasta)
    except RaApiConnectionError as error:
        return _error_historico(RAAPI_UNAVAILABLE, error.message)
    except RaApiHttpError as error:
        codigo = RAAPI_REJECTED if error.status_code == 400 else RAAPI_ERROR
        return _error_historico(codigo, _mensaje_http(error))
    except RaApiResponseError as error:
        return _error_historico(RAAPI_ERROR, error.message)

    pedidos = body["pedidos"]
    fecha_respuesta_desde = body.get("fecha_desde")
    fecha_respuesta_hasta = body.get("fecha_hasta")
    if not pedidos and fecha_respuesta_desde is None and fecha_respuesta_hasta is None:
        mensaje = "No hay pedidos registrados."
    elif not pedidos:
        mensaje = "No se encontraron pedidos para las fechas indicadas."
    else:
        mensaje = "Pedidos históricos del período indicado."

    return {
        "success": True,
        "fecha_desde": fecha_respuesta_desde,
        "fecha_hasta": fecha_respuesta_hasta,
        "pedidos": pedidos,
        "estadisticas": _estadisticas(pedidos),
        "message": mensaje,
    }


def _rango_fechas(desde: str | None, hasta: str | None) -> tuple[str | None, str | None]:
    fecha_desde = _fecha_o_vacia(desde, "desde")
    fecha_hasta = _fecha_o_vacia(hasta, "hasta")
    if (fecha_desde is None) != (fecha_hasta is None):
        raise ValueError("Indicá la fecha desde y la fecha hasta.")
    if fecha_desde is not None and fecha_hasta is not None and fecha_desde > fecha_hasta:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return fecha_desde, fecha_hasta


def _fecha_o_vacia(value: str | None, nombre: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"La fecha {nombre} no es válida. Usá YYYY-MM-DD.")
    texto = value.strip()
    if not texto:
        return None
    if _FECHA.fullmatch(texto) is None:
        raise ValueError(f"La fecha {nombre} no es válida. Usá YYYY-MM-DD.")
    try:
        date.fromisoformat(texto)
    except ValueError as error:
        raise ValueError(f"La fecha {nombre} no es válida. Usá YYYY-MM-DD.") from error
    return texto


def _estadisticas(pedidos: list[dict]) -> dict:
    cantidad_total = 0.0
    cantidad_vendida = 0.0
    valor_total = 0.0
    for pedido in pedidos:
        cantidad = _numero(pedido.get("cantidad"))
        precio = _numero(pedido.get("precio_unitario"))
        cantidad_total += cantidad
        if not _es_regalo(pedido.get("es_regalo")):
            cantidad_vendida += cantidad
            valor_total += cantidad * precio
    return {
        "cantidad_total": round(cantidad_total, 1),
        "cantidad_vendida": round(cantidad_vendida, 1),
        "valor_total": round(valor_total, 2),
    }


def _numero(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    if not math.isfinite(value):
        return 0.0
    return float(value)


def _es_regalo(value: Any) -> bool:
    return not isinstance(value, bool) and value == 1


def _cliente_busqueda(fila: dict) -> dict:
    if "id" not in fila:
        raise ValueError("raapi devolvió un cliente sin id.")
    cliente = {"id_cliente": fila["id"]}
    for campo in _CAMPOS_BUSQUEDA:
        cliente[campo] = fila.get(campo)
    return cliente


def _es_entero_positivo(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _es_cantidad_valida(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value) and value > 0


def _codigo_http(error: RaApiHttpError) -> str:
    if error.status_code == 404:
        return CLIENT_NOT_FOUND
    if error.status_code == 400:
        return RAAPI_REJECTED
    return RAAPI_ERROR


def _mensaje_http(error: RaApiHttpError) -> str:
    return mensaje_de_cuerpo(error.body) or error.message


def _mensaje_pedido_http(error: RaApiHttpError) -> str:
    if error.status_code == 404:
        return "No existe el cliente indicado."
    return _mensaje_http(error)


def _error_busqueda(error_code: str, message: str) -> dict:
    return {
        "status": ERROR,
        "success": False,
        "error_code": error_code,
        "message": message,
        "clientes": [],
    }


def _error_pedido(
    error_code: str,
    message: str,
    *,
    id_cliente: int | None = None,
    detalle: str | None = None,
) -> dict:
    payload = {
        "success": False,
        "error_code": error_code,
        "message": message,
    }
    if id_cliente is not None:
        payload["id_cliente"] = id_cliente
    if detalle and detalle != message:
        payload["detalle"] = detalle
    return payload


def _error_historico(error_code: str, message: str) -> dict:
    return {
        "success": False,
        "error_code": error_code,
        "message": message,
        "fecha_desde": None,
        "fecha_hasta": None,
        "pedidos": [],
        "estadisticas": dict(ESTADISTICAS_VACIAS),
    }
