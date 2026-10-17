"""Bootstrap DEV del realm rancho.

Idempotente. No crea el realm, los clientes, los scopes ni los roles:
eso entra por --import-realm desde rancho-realm.json.
Este script solo escribe datos que no se versionan: el secret de ra-mcp,
el usuario DEV y sus role mappings.
Usa el Admin API del realm master. No habilita Direct Access Grants en rancho.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def _exigir(nombre: str) -> str:
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        print(f"Falta {nombre}", file=sys.stderr)
        raise SystemExit(1)
    return valor


BASE = os.environ.get("KEYCLOAK_INTERNAL_URL", "http://keycloak:8080").rstrip("/")
ADMIN_USER = _exigir("KEYCLOAK_ADMIN")
ADMIN_PASSWORD = _exigir("KEYCLOAK_ADMIN_PASSWORD")
DEMO_USER = os.environ.get("RANCHO_DEMO_USER", "rancho").strip() or "rancho"
DEMO_PASSWORD = _exigir("RANCHO_DEMO_PASSWORD")
CLIENT_SECRET = _exigir("KEYCLOAK_CLIENT_SECRET")
REALM = "rancho"
ROLES = ("clientes:read", "pedidos:write")


def _request(method: str, url: str, token: str | None = None, body: dict | list | None = None, form: dict | None = None):
    data = None
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            if not raw:
                return response.status, None
            return response.status, json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} -> HTTP {error.code}: {detalle}") from error


def _admin_token() -> str:
    _, payload = _request(
        "POST",
        f"{BASE}/realms/master/protocol/openid-connect/token",
        form={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASSWORD,
        },
    )
    return payload["access_token"]


def _esperar_realm(token_fn) -> str:
    ultimo = None
    for _ in range(60):
        try:
            token = token_fn()
            _request("GET", f"{BASE}/admin/realms/{REALM}", token)
            return token
        except Exception as error:  # noqa: BLE001 - reintento de arranque
            ultimo = error
            time.sleep(2)
    raise RuntimeError(f"Keycloak no expuso el realm {REALM}: {ultimo}")


def _cliente(token: str, client_id: str) -> dict:
    _, clientes = _request("GET", f"{BASE}/admin/realms/{REALM}/clients?clientId={urllib.parse.quote(client_id)}", token)
    coincidencias = [item for item in clientes if item.get("clientId") == client_id]
    if len(coincidencias) != 1:
        raise RuntimeError(f"No se encontró un único cliente {client_id}")
    return coincidencias[0]


def _fijar_secret(token: str, client_uuid: str) -> None:
    _, cliente = _request("GET", f"{BASE}/admin/realms/{REALM}/clients/{client_uuid}", token)
    cliente["secret"] = CLIENT_SECRET
    cliente["publicClient"] = False
    cliente["directAccessGrantsEnabled"] = False
    cliente["implicitFlowEnabled"] = False
    _request("PUT", f"{BASE}/admin/realms/{REALM}/clients/{client_uuid}", token, cliente)


def _usuario(token: str) -> str:
    consulta = urllib.parse.urlencode({"username": DEMO_USER, "exact": "true"})
    _, usuarios = _request("GET", f"{BASE}/admin/realms/{REALM}/users?{consulta}", token)
    if usuarios:
        user_id = usuarios[0]["id"]
    else:
        status, _ = _request(
            "POST",
            f"{BASE}/admin/realms/{REALM}/users",
            token,
            {
                "username": DEMO_USER,
                "enabled": True,
                "email": "rancho@example.com",
                "emailVerified": True,
                "firstName": "Rancho",
                "lastName": "Demo",
            },
        )
        if status not in (201, 204):
            raise RuntimeError(f"No se pudo crear el usuario DEV (HTTP {status})")
        _, usuarios = _request("GET", f"{BASE}/admin/realms/{REALM}/users?{consulta}", token)
        if not usuarios:
            raise RuntimeError("El usuario DEV no apareció después de crearlo")
        user_id = usuarios[0]["id"]
    _, actual = _request("GET", f"{BASE}/admin/realms/{REALM}/users/{user_id}", token)
    actual.update(
        {
            "firstName": "Rancho",
            "lastName": "Demo",
            "email": "rancho@example.com",
            "emailVerified": True,
            "enabled": True,
            "requiredActions": [],
        }
    )
    _request("PUT", f"{BASE}/admin/realms/{REALM}/users/{user_id}", token, actual)
    _request(
        "PUT",
        f"{BASE}/admin/realms/{REALM}/users/{user_id}/reset-password",
        token,
        {"type": "password", "value": DEMO_PASSWORD, "temporary": False},
    )
    return user_id


def _asignar_roles(token: str, user_id: str, raapi_uuid: str) -> None:
    _, roles = _request("GET", f"{BASE}/admin/realms/{REALM}/clients/{raapi_uuid}/roles", token)
    pedidos = [rol for rol in roles if rol.get("name") in ROLES]
    if {rol["name"] for rol in pedidos} != set(ROLES):
        raise RuntimeError(f"Faltan roles de raapi. Encontrados: {[rol.get('name') for rol in roles]}")
    _request(
        "POST",
        f"{BASE}/admin/realms/{REALM}/users/{user_id}/role-mappings/clients/{raapi_uuid}",
        token,
        [{"id": rol["id"], "name": rol["name"]} for rol in pedidos],
    )


def main() -> None:
    token = _esperar_realm(_admin_token)
    ra_mcp = _cliente(token, "ra-mcp")
    raapi = _cliente(token, "raapi")
    _fijar_secret(token, ra_mcp["id"])
    user_id = _usuario(token)
    _asignar_roles(token, user_id, raapi["id"])
    print(f"Bootstrap DEV listo: usuario {DEMO_USER}, roles {', '.join(ROLES)}, secret de ra-mcp actualizado")


if __name__ == "__main__":
    main()
