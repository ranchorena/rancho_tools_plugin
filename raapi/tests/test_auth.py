"""Protección JWT de raapi sin base de datos.

Los tokens se firman con una clave de prueba. El middleware es el mismo
que instala server.py.
"""

import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, jsonify

from auth import AuthError, decodificar_token, instalar_autenticacion

ISSUER = "http://localhost:8081/realms/rancho"
OTRO_ISSUER = "http://localhost:8081/realms/otro"


@pytest.fixture(scope="module")
def claves():
    privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return privada, privada.public_key()


@pytest.fixture
def entorno(monkeypatch):
    monkeypatch.setenv("KEYCLOAK_ISSUER", ISSUER)
    monkeypatch.setenv("KEYCLOAK_JWKS_URL", "http://keycloak.test/jwks")
    monkeypatch.setenv("RA_API_AUDIENCE", "raapi")


def token(privada, *, aud="raapi", iss=ISSUER, roles=("clientes:read", "pedidos:write"), exp=None, sub="user-1"):
    ahora = int(time.time())
    return jwt.encode(
        {
            "iss": iss,
            "aud": aud,
            "azp": "raweb",
            "sub": sub,
            "preferred_username": "rancho",
            "email": "rancho@example.com",
            "exp": ahora + 300 if exp is None else exp,
            "iat": ahora,
            "resource_access": {"raapi": {"roles": list(roles)}},
        },
        privada,
        algorithm="RS256",
    )


@pytest.fixture
def cliente(entorno, claves):
    privada, publica = claves

    def decoder(valor):
        return decodificar_token(valor, key_resolver=lambda _token: publica)

    app = Flask(__name__)
    instalar_autenticacion(app, decoder=decoder)

    @app.route("/api/clientes/buscar", methods=["POST"])
    def buscar_clientes_api():
        return jsonify({"ok": True})

    @app.route("/api/clientes/actualizar/<int:cliente_id>", methods=["PUT"])
    def actualizar_cliente_api(cliente_id):
        return jsonify({"ok": True, "cliente_id": cliente_id})

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app.test_client(), privada


def test_health_publico(cliente):
    http, _ = cliente
    respuesta = http.get("/health")
    assert respuesta.status_code == 200


def test_sin_authorization(cliente):
    http, _ = cliente
    respuesta = http.post("/api/clientes/buscar", json={})
    assert respuesta.status_code == 401
    assert "Bearer" in respuesta.get_json()["error"]


def test_bearer_invalido(cliente):
    http, _ = cliente
    respuesta = http.post("/api/clientes/buscar", headers={"Authorization": "Bearer no-es-un-jwt"})
    assert respuesta.status_code == 401


def test_token_expirado(cliente):
    http, privada = cliente
    respuesta = http.post(
        "/api/clientes/buscar",
        headers={"Authorization": f"Bearer {token(privada, exp=int(time.time()) - 60)}"},
    )
    assert respuesta.status_code == 401
    assert "expir" in respuesta.get_json()["error"]


def test_issuer_incorrecto(cliente):
    http, privada = cliente
    respuesta = http.post(
        "/api/clientes/buscar",
        headers={"Authorization": f"Bearer {token(privada, iss=OTRO_ISSUER)}"},
    )
    assert respuesta.status_code == 401


def test_audience_incorrecta(cliente):
    http, privada = cliente
    respuesta = http.post(
        "/api/clientes/buscar",
        headers={"Authorization": f"Bearer {token(privada, aud='ra-mcp')}"},
    )
    assert respuesta.status_code == 401
    assert "audiencia" in respuesta.get_json()["error"]


def test_audience_raapi_aceptada(cliente):
    http, privada = cliente
    respuesta = http.post(
        "/api/clientes/buscar",
        headers={"Authorization": f"Bearer {token(privada, aud=['raapi', 'account'])}"},
    )
    assert respuesta.status_code == 200


def test_busqueda_sin_clientes_read(cliente):
    http, privada = cliente
    respuesta = http.post(
        "/api/clientes/buscar",
        headers={"Authorization": f"Bearer {token(privada, roles=['pedidos:write'])}"},
    )
    assert respuesta.status_code == 403


def test_busqueda_con_clientes_read(cliente):
    http, privada = cliente
    respuesta = http.post(
        "/api/clientes/buscar",
        headers={"Authorization": f"Bearer {token(privada, roles=['clientes:read'])}"},
    )
    assert respuesta.status_code == 200


def test_alta_sin_pedidos_write(cliente):
    http, privada = cliente
    respuesta = http.put(
        "/api/clientes/actualizar/1",
        headers={"Authorization": f"Bearer {token(privada, roles=['clientes:read'])}"},
        json={"tiene_pedido": True},
    )
    assert respuesta.status_code == 403


def test_alta_con_pedidos_write(cliente):
    http, privada = cliente
    respuesta = http.put(
        "/api/clientes/actualizar/1",
        headers={"Authorization": f"Bearer {token(privada, roles=['pedidos:write'])}"},
        json={"tiene_pedido": True},
    )
    assert respuesta.status_code == 200


def test_decodificar_rechaza_error_de_configuracion(monkeypatch):
    monkeypatch.delenv("KEYCLOAK_ISSUER", raising=False)
    monkeypatch.delenv("KEYCLOAK_JWKS_URL", raising=False)
    with pytest.raises(AuthError) as error:
        decodificar_token("x")
    assert error.value.status == 500
