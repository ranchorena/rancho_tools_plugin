"""Cliente HTTP de raapi.

ra-mcp no abre conexiones a la base ni importa Flask. Toda lectura y
persistencia pasa por los endpoints ya expuestos por raapi.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable


class RaApiConnectionError(Exception):
    """No hubo respuesta HTTP de raapi."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class RaApiHttpError(Exception):
    """raapi respondió un estado de error."""

    def __init__(self, status_code: int, body: Any) -> None:
        self.status_code = status_code
        self.body = body
        self.message = mensaje_de_cuerpo(body) or f"raapi respondió HTTP {status_code}."
        super().__init__(self.message)


class RaApiResponseError(Exception):
    """raapi respondió 2xx con un cuerpo que no es el contrato esperado."""

    def __init__(self, message: str, body: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.body = body


Transport = Callable[..., tuple[int, Any]]


def mensaje_de_cuerpo(body: Any) -> str | None:
    if isinstance(body, dict):
        for key in ("error", "mensaje", "message"):
            value = body.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    if isinstance(body, str) and body.strip():
        return body.strip()
    return None


def urllib_transport(
    method: str,
    url: str,
    body: dict | None,
    timeout: float,
    headers: dict | None = None,
) -> tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=request_headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, _parse_body(response.read())
    except urllib.error.HTTPError as error:
        return error.code, _parse_body(error.read())
    except urllib.error.URLError as error:
        reason = getattr(error, "reason", error)
        raise RaApiConnectionError(f"No se pudo comunicar con raapi: {reason}") from error
    except TimeoutError as error:
        raise RaApiConnectionError("No se pudo comunicar con raapi: tiempo de espera agotado.") from error


def _parse_body(raw: bytes) -> Any:
    if not raw:
        return None
    text = raw.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


class RaApiClient:
    """Adaptador HTTP hacia los endpoints de clientes de raapi."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        transport: Transport | None = None,
        token_provider: Callable[[], str] | None = None,
    ) -> None:
        normalized = (base_url or "").strip().rstrip("/")
        if not normalized:
            raise ValueError("RA_API_BASE_URL es requerida.")
        self.base_url = normalized
        self.timeout = timeout
        self._transport = transport or urllib_transport
        self._token_provider = token_provider

    def buscar_por_nombre(self, nombre: str) -> list[dict]:
        """POST /api/clientes/buscar con criterio nombre.

        raapi responde HTTP 200 y un array, también cuando no hay coincidencias.
        """
        body = self._request(
            "POST",
            "/api/clientes/buscar",
            {"criterio": "nombre", "nombre_cliente": nombre},
        )
        if not isinstance(body, list):
            raise RaApiResponseError(
                "raapi no devolvió la lista de clientes esperada.",
                body,
            )
        if not all(isinstance(item, dict) for item in body):
            raise RaApiResponseError(
                "raapi devolvió coincidencias con un formato inesperado.",
                body,
            )
        return body

    def registrar_pedido(self, id_cliente: int, cantidad_docenas: float, nro_pao: int) -> dict:
        """PUT /api/clientes/actualizar/<id> solo con los campos del pedido.

        El DTO de actualización traduce docenas -> cantidad. Enviar únicamente
        estos campos evita pisar horario, observaciones o es_regalo, que el
        formulario web reenvía porque la búsqueda no los trae.
        """
        body = self._request(
            "PUT",
            f"/api/clientes/actualizar/{id_cliente}",
            {
                "docenas": cantidad_docenas,
                "nro_pao": nro_pao,
                "tiene_pedido": True,
            },
        )
        if not isinstance(body, dict) or not isinstance(body.get("mensaje"), str):
            raise RaApiResponseError(
                "raapi no confirmó la actualización del pedido.",
                body,
            )
        return body

    def pedidos_historico(self, desde: str | None = None, hasta: str | None = None) -> dict:
        """GET /api/pedidos/historico.

        Sin fechas, raapi usa el día del pedido más reciente. Con fechas, el
        rango incluye ambos días.
        """
        consulta: dict[str, str] = {}
        if desde is not None:
            consulta["desde"] = desde
        if hasta is not None:
            consulta["hasta"] = hasta
        path = "/api/pedidos/historico"
        if consulta:
            path = f"{path}?{urllib.parse.urlencode(consulta)}"
        body = self._request("GET", path, None)
        if not isinstance(body, dict):
            raise RaApiResponseError(
                "raapi no devolvió el historial de pedidos esperado.",
                body,
            )
        pedidos = body.get("pedidos")
        if not isinstance(pedidos, list) or not all(isinstance(item, dict) for item in pedidos):
            raise RaApiResponseError(
                "raapi devolvió pedidos con un formato inesperado.",
                body,
            )
        if "fecha_desde" not in body or "fecha_hasta" not in body:
            raise RaApiResponseError(
                "raapi no informó las fechas del historial.",
                body,
            )
        return body

    def _request(self, method: str, path: str, body: dict | None) -> Any:
        if self._token_provider:
            headers = {"Authorization": f"Bearer {self._token_provider()}"}
            status, payload = self._transport(method, f"{self.base_url}{path}", body, self.timeout, headers)
        else:
            status, payload = self._transport(method, f"{self.base_url}{path}", body, self.timeout)
        if status >= 400:
            raise RaApiHttpError(status, payload)
        return payload
