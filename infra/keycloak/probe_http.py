"""Prueba HTTP de la frontera raapi con tokens reales de Keycloak.

Llama a raapi ya levantado en el puerto 5000 con tokens de Authorization
Code. No inicia otro servidor.
"""

from __future__ import annotations

import json
import os
import secrets
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "infra" / "keycloak"))
USUARIO_SIN_ROLES = "rancho-sin-permisos"


def _cargar_env() -> None:
    for linea in (RAIZ / ".env").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())
    os.environ["KEYCLOAK_URL"] = "http://localhost:8081"
    os.environ["KEYCLOAK_ISSUER"] = "http://localhost:8081/realms/rancho"
    os.environ["KEYCLOAK_JWKS_URL"] = "http://127.0.0.1:8081/realms/rancho/protocol/openid-connect/certs"
    os.environ.setdefault("RA_API_AUDIENCE", "raapi")
    os.environ.setdefault("CORS_ORIGINS", "http://localhost:8080")
    os.environ["FLASK_DEBUG"] = "0"


API = "http://127.0.0.1:5000"


def _http(method: str, path: str, token: str | None = None, body: dict | None = None, origin: str | None = None):
    headers = {"Accept": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if origin:
        headers["Origin"] = origin
        headers["Access-Control-Request-Method"] = "POST"
        headers["Access-Control-Request-Headers"] = "authorization,content-type"
    request = urllib.request.Request(f"{API}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else None, response.headers
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
        return error.code, payload, error.headers


def _id_por_username(username: str) -> str | None:
    consulta = urllib.parse.urlencode({"username": username, "exact": "true"})
    _, usuarios = verify_dev._admin_json("GET", f"{PUBLIC}/admin/realms/rancho/users?{consulta}")
    for usuario in usuarios or []:
        if usuario.get("username") == username:
            return usuario["id"]
    return None


def _usuario_sin_roles(raapi_id: str) -> str:
    user_id = _id_por_username(USUARIO_SIN_ROLES)
    if user_id is None:
        verify_dev._admin_json(
            "POST",
            f"{PUBLIC}/admin/realms/rancho/users",
            {
                "username": USUARIO_SIN_ROLES,
                "email": "sin-permisos@example.com",
                "firstName": "Sin",
                "lastName": "Permisos",
                "enabled": True,
                "emailVerified": True,
                "requiredActions": [],
            },
        )
        user_id = _id_por_username(USUARIO_SIN_ROLES)
    if user_id is None:
        raise SystemExit("no se pudo crear el usuario sin roles")
    verify_dev._admin_json(
        "PUT",
        f"{PUBLIC}/admin/realms/rancho/users/{user_id}",
        {
            "username": USUARIO_SIN_ROLES,
            "email": "sin-permisos@example.com",
            "firstName": "Sin",
            "lastName": "Permisos",
            "enabled": True,
            "emailVerified": True,
            "requiredActions": [],
        },
    )
    clave = secrets.token_urlsafe(18)
    verify_dev._admin_json(
        "PUT",
        f"{PUBLIC}/admin/realms/rancho/users/{user_id}/reset-password",
        {"type": "password", "value": clave, "temporary": False},
    )
    _, asignados = verify_dev._admin_json(
        "GET",
        f"{PUBLIC}/admin/realms/rancho/users/{user_id}/role-mappings/clients/{raapi_id}",
    )
    if asignados:
        verify_dev._admin_json(
            "DELETE",
            f"{PUBLIC}/admin/realms/rancho/users/{user_id}/role-mappings/clients/{raapi_id}",
            asignados,
        )
    return clave


def _restaurar_demo() -> None:
    user_id = _id_por_username(verify_dev.DEMO_USER)
    if user_id is None:
        raise SystemExit("el usuario DEV no existe")
    verify_dev._admin_json(
        "PUT",
        f"{PUBLIC}/admin/realms/rancho/users/{user_id}/reset-password",
        {"type": "password", "value": verify_dev.DEMO_PASSWORD, "temporary": False},
    )


def _borrar_usuario() -> None:
    user_id = _id_por_username(USUARIO_SIN_ROLES)
    if user_id:
        verify_dev._admin_json("DELETE", f"{PUBLIC}/admin/realms/rancho/users/{user_id}")


def _exigir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        print(f"FALLO: {mensaje}", file=sys.stderr)
        raise SystemExit(1)
    print(mensaje)


def _verificar_verifier(token_raweb: str, token_mcp: str) -> None:
    script = r"""
import asyncio, json, os, sys
from fastmcp.server.auth.providers.jwt import JWTVerifier
tokens = json.loads(sys.stdin.read())
verifier = JWTVerifier(
    jwks_uri=os.environ["KEYCLOAK_JWKS_URL"],
    issuer=os.environ["KEYCLOAK_ISSUER"],
    audience="ra-mcp",
)
async def run():
    rechazado = await verifier.verify_token(tokens["raweb"])
    aceptado = await verifier.verify_token(tokens["mcp"])
    print(json.dumps({
        "raweb_rechazado": rechazado is None,
        "mcp_aceptado": aceptado is not None and aceptado.token == tokens["mcp"],
        "mcp_aud": None if aceptado is None else aceptado.claims.get("aud"),
    }))
asyncio.run(run())
"""
    import subprocess

    entorno = os.environ.copy()
    entorno["KEYCLOAK_JWKS_URL"] = os.environ["KEYCLOAK_JWKS_URL"]
    entorno["KEYCLOAK_ISSUER"] = os.environ["KEYCLOAK_ISSUER"]
    python = RAIZ / "ra-mcp" / ".venv" / "Scripts" / "python.exe"
    resultado = subprocess.run(
        [str(python), "-c", script],
        input=json.dumps({"raweb": token_raweb, "mcp": token_mcp}),
        text=True,
        capture_output=True,
        env=entorno,
        check=False,
    )
    if resultado.returncode != 0:
        print(resultado.stderr[-800:], file=sys.stderr)
        raise SystemExit(1)
    print(resultado.stdout.strip())
    datos = json.loads(resultado.stdout)
    _exigir(datos["raweb_rechazado"], "JWTVerifier aud=ra-mcp rechaza el token de raweb")
    _exigir(datos["mcp_aceptado"], "JWTVerifier aud=ra-mcp acepta el token upstream y conserva ese JWT")


def _solo_ipv4() -> None:
    original = socket.getaddrinfo

    def getaddrinfo(host, port, *args, **kwargs):
        return [item for item in original(host, port, *args, **kwargs) if item[0] == socket.AF_INET]

    socket.getaddrinfo = getaddrinfo


def main() -> None:
    global verify_dev, PUBLIC
    _solo_ipv4()
    _cargar_env()
    import verify_dev as modulo

    verify_dev = modulo
    PUBLIC = modulo.PUBLIC
    print("inicio probe", flush=True)
    estado, _, _ = _http("GET", "/health")
    print("health", estado, flush=True)
    if estado != 200:
        raise SystemExit("raapi no responde en el puerto 5000")

    raapi = verify_dev._cliente("raapi")
    _restaurar_demo()
    clave = _usuario_sin_roles(raapi["id"])
    try:
        web = verify_dev._token_authorization_code("raweb", "http://localhost:8080/")
        limitado = verify_dev._token_authorization_code(
            "raweb",
            "http://localhost:8080/",
            username=USUARIO_SIN_ROLES,
            password=clave,
        )
        mcp = verify_dev._token_authorization_code(
            "ra-mcp",
            "http://localhost:8000/auth/callback",
            verify_dev.CLIENT_SECRET,
        )
        _, exchanged = verify_dev._json(
            "POST",
            f"{verify_dev.ISSUER}/protocol/openid-connect/token",
            form={
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "client_id": "ra-mcp",
                "client_secret": verify_dev.CLIENT_SECRET,
                "subject_token": mcp["access_token"],
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "audience": "raapi",
            },
        )
    finally:
        _borrar_usuario()

    web_token = web["access_token"]
    limitado_token = limitado["access_token"]
    down = exchanged["access_token"]
    _exigir(down != mcp["access_token"], "el token intercambiado es distinto del upstream")

    estado, _, _ = _http("GET", "/health")
    _exigir(estado == 200, "GET /health sin token -> 200")
    estado, cuerpo, _ = _http("POST", "/api/clientes/buscar", body={"criterio": "nombre", "nombre_cliente": "Silvia"})
    _exigir(estado == 401 and cuerpo.get("error"), f"POST sin token -> 401 ({cuerpo})")
    estado, _, _ = _http("POST", "/api/clientes/buscar", token="no-es-jwt", body={"criterio": "nombre", "nombre_cliente": "Silvia"})
    _exigir(estado == 401, "POST bearer inválido -> 401")
    alterado = web_token[:-2] + ("a" if not web_token.endswith("a") else "b")
    estado, _, _ = _http("POST", "/api/clientes/buscar", token=alterado, body={"criterio": "nombre", "nombre_cliente": "Silvia"})
    _exigir(estado == 401, "POST token alterado -> 401")
    web_claims = verify_dev._claims(web_token)
    down_claims = verify_dev._claims(down)
    print(json.dumps(verify_dev._resumen(web_claims, "raweb"), ensure_ascii=False))
    print(json.dumps(verify_dev._resumen(down_claims, "token-exchange"), ensure_ascii=False))
    _exigir(web_claims.get("azp") == "raweb" and web_claims.get("aud") == "raapi", "claims raweb")
    _exigir(down_claims.get("aud") == "raapi" and down_claims.get("sub") == web_claims.get("sub"), "claims exchange")
    estado, cuerpo, _ = _http("POST", "/api/clientes/buscar", token=web_token, body={"criterio": "nombre", "nombre_cliente": "Silvia"})
    _exigir(
        estado == 200 and isinstance(cuerpo, list),
        f"POST raweb con clientes:read -> 200 ({estado}, {cuerpo if isinstance(cuerpo, dict) else type(cuerpo).__name__})",
    )
    estado, cuerpo, _ = _http("POST", "/api/clientes/buscar", token=limitado_token, body={"criterio": "nombre", "nombre_cliente": "Silvia"})
    _exigir(estado == 403, f"POST sin clientes:read -> 403 ({cuerpo})")
    estado, _, _ = _http("GET", "/api/pedidos/historico", token=limitado_token)
    _exigir(estado == 403, "GET historico sin clientes:read -> 403")
    estado, cuerpo, _ = _http("PUT", "/api/clientes/actualizar/1", token=limitado_token, body={})
    _exigir(estado == 403, f"PUT sin pedidos:write -> 403 ({cuerpo})")
    estado, cuerpo, _ = _http("POST", "/api/clientes/buscar", token=down, body={"criterio": "nombre", "nombre_cliente": "Silvia"})
    _exigir(estado == 200 and isinstance(cuerpo, list), f"POST con token intercambiado -> 200 ({estado})")
    estado, _, headers = _http("OPTIONS", "/api/clientes/buscar", origin="http://localhost:8080")
    permitido = headers.get("Access-Control-Allow-Origin")
    _exigir(estado in (200, 204) and permitido == "http://localhost:8080", f"CORS origen exacto ({permitido})")
    _exigir(headers.get("Access-Control-Allow-Origin") != "*", "CORS no usa comodín")
    _verificar_verifier(web_token, mcp["access_token"])
    print("PROBE HTTP listo")


if __name__ == "__main__":
    main()
