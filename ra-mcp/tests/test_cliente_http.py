"""Cliente HTTP real contra un raapi simulado en localhost."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from ra_mcp.client import RaApiClient, RaApiConnectionError


class _ApiSimulada(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        self._leer()
        self._json(200, [{"id": 220, "nombre": "Marta López", "direccion": "Sarmiento 550", "calle": "Sarmiento", "altura": 550, "longitud": -58.4, "latitud": -34.6}])

    def do_PUT(self):  # noqa: N802
        body = self._leer()
        assert self.path == "/api/clientes/actualizar/220"
        assert body == {"docenas": 1, "nro_pao": 5, "tiene_pedido": True}
        self._json(200, {"mensaje": "Cliente actualizado correctamente."})

    def do_GET(self):  # noqa: N802
        assert self.path == "/api/pedidos/historico"
        self._json(
            200,
            {
                "fecha_desde": "2026-10-11",
                "fecha_hasta": "2026-10-11",
                "pedidos": [],
            },
        )

    def _leer(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        return json.loads(raw.decode("utf-8")) if raw else None

    def _json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):  # noqa: A003
        return


@pytest.fixture
def api_simulada():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ApiSimulada)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        thread.join(timeout=3)


def test_cliente_http_busca_y_registra(api_simulada):
    client = RaApiClient(api_simulada, timeout=2)

    encontrados = client.buscar_por_nombre("Marta")
    confirmacion = client.registrar_pedido(220, 1, 5)

    assert encontrados[0]["id"] == 220
    assert confirmacion["mensaje"] == "Cliente actualizado correctamente."
    assert client.pedidos_historico()["fecha_desde"] == "2026-10-11"


def test_puerto_cerrado_es_error_de_comunicacion():
    client = RaApiClient("http://127.0.0.1:9", timeout=1)

    with pytest.raises(RaApiConnectionError):
        client.buscar_por_nombre("Silvia")
