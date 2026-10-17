"""Comprueba Keycloak DEV: realm, clientes, theme, usuario y tokens reales.

No usa Direct Access Grants del realm rancho. El access token se obtiene
con Authorization Code + PKCE, igual que el navegador, leyendo el code del
redirect sin seguirlo.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import http.cookiejar


PUBLIC = os.environ.get("KEYCLOAK_URL", "http://localhost:8081").rstrip("/")
ISSUER = f"{PUBLIC}/realms/rancho"
ADMIN_USER = os.environ.get("KEYCLOAK_ADMIN", "")
ADMIN_PASSWORD = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "")
DEMO_USER = os.environ.get("RANCHO_DEMO_USER", "rancho")
DEMO_PASSWORD = os.environ.get("RANCHO_DEMO_PASSWORD", "")
CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET", "")


class RedirectDetenido(Exception):
    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.url = url


class _CookiesLocalhost(urllib.request.HTTPCookieProcessor):
    """Keycloak marca la cookie de sesión como Secure en localhost.

    Los navegadores la aceptan en http://localhost. urllib no la reenvía
    salvo que el flag Secure se ignore para ese host.
    """

    def http_request(self, request):
        host = urllib.parse.urlparse(request.full_url).hostname
        originales = []
        if host in {"localhost", "127.0.0.1"}:
            for cookie in self.cookiejar:
                originales.append((cookie, cookie.secure))
                cookie.secure = False
        try:
            return super().http_request(request)
        finally:
            for cookie, secure in originales:
                cookie.secure = secure

    https_request = http_request
    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.url = url


class _Redirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, prefijo: str) -> None:
        self.prefijo = prefijo

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if newurl.startswith(self.prefijo):
            raise RedirectDetenido(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fallo(mensaje: str) -> None:
    print(f"FALLO: {mensaje}", file=sys.stderr)
    raise SystemExit(1)


def _json(method: str, url: str, token: str | None = None, body=None, form=None):
    headers = {"Accept": "application/json"}
    data = None
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
            return response.status, json.loads(raw.decode("utf-8")) if raw else None
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")
        _fallo(f"{method} {url} HTTP {error.code}: {detalle[:500]}")


def _admin() -> str:
    _, payload = _json(
        "POST",
        f"{PUBLIC}/realms/master/protocol/openid-connect/token",
        form={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASSWORD,
        },
    )
    return payload["access_token"]


def _admin_json(method: str, url: str, body=None):
    token = _admin()
    return _json(method, url, token, body)


def _cliente(client_id: str) -> dict:
    _, clientes = _admin_json("GET", f"{PUBLIC}/admin/realms/rancho/clients?clientId={urllib.parse.quote(client_id)}")
    encontrados = [item for item in clientes if item.get("clientId") == client_id]
    if len(encontrados) != 1:
        _fallo(f"cliente {client_id} no encontrado")
    return encontrados[0]


def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(48)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def _token_authorization_code(
    client_id: str,
    redirect_uri: str,
    client_secret: str | None = None,
    username: str | None = None,
    password: str | None = None,
) -> dict:
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(16)
    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": redirect_uri,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
        }
    )
    jar = http.cookiejar.CookieJar()
    redirect = _Redirect(redirect_uri)
    opener = urllib.request.build_opener(_CookiesLocalhost(jar), redirect)
    inicio = opener.open(f"{ISSUER}/protocol/openid-connect/auth?{query}", timeout=90)
    html = inicio.read().decode("utf-8", errors="replace")
    accion = _accion_login(html)
    form = urllib.parse.urlencode(
        {
            "username": username or DEMO_USER,
            "password": password or DEMO_PASSWORD,
            "credentialId": "",
        }
    ).encode("utf-8")
    post = urllib.request.Request(accion, data=form, method="POST")
    try:
        respuesta = opener.open(post, timeout=90)
    except RedirectDetenido as detenido:
        destino = detenido.url
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")
        _fallo(f"login de {client_id} HTTP {error.code}: {detalle[:300]}")
    else:
        cuerpo = respuesta.read().decode("utf-8", errors="replace")
        _fallo(f"el login de {client_id} no redirigió a {redirect_uri}. url={respuesta.geturl()} cuerpo={cuerpo[:300]}")
    parsed = urllib.parse.urlparse(destino)
    params = urllib.parse.parse_qs(parsed.query)
    if "code" not in params:
        _fallo(f"redirect de {client_id} sin code: {parsed.query}")
    token_form = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": params["code"][0],
        "redirect_uri": redirect_uri,
        "code_verifier": verifier,
    }
    if client_secret:
        token_form["client_secret"] = client_secret
    _, tokens = _json("POST", f"{ISSUER}/protocol/openid-connect/token", form=token_form)
    return tokens


def _accion_login(html: str) -> str:
    marcador = 'action="'
    inicio = html.find(marcador)
    if inicio < 0:
        _fallo("la página de login no tiene formulario")
    inicio += len(marcador)
    fin = html.find('"', inicio)
    accion = html[inicio:fin].replace("&amp;", "&")
    if accion.startswith("/"):
        return f"{PUBLIC}{accion}"
    return accion


def _claims(jwt: str) -> dict:
    parte = jwt.split(".")[1]
    parte += "=" * (-len(parte) % 4)
    return json.loads(base64.urlsafe_b64decode(parte.encode("ascii")))


def _aud_incluye(claims: dict, esperado: str) -> bool:
    aud = claims.get("aud")
    if isinstance(aud, list):
        return esperado in aud
    return aud == esperado


def _roles(claims: dict) -> list:
    return ((claims.get("resource_access") or {}).get("raapi") or {}).get("roles") or []


def main() -> None:
    if not ADMIN_USER or not ADMIN_PASSWORD or not DEMO_PASSWORD or not CLIENT_SECRET:
        _fallo("faltan KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD, RANCHO_DEMO_PASSWORD o KEYCLOAK_CLIENT_SECRET")

    _, discovery = _json("GET", f"{ISSUER}/.well-known/openid-configuration")
    if discovery.get("issuer") != ISSUER:
        _fallo(f"issuer inesperado: {discovery.get('issuer')}")
    _, jwks = _json("GET", discovery["jwks_uri"])
    if not jwks.get("keys"):
        _fallo("JWKS vacío")
    print("discovery y JWKS responden")

    _, realm = _admin_json("GET", f"{PUBLIC}/admin/realms/rancho")
    if realm.get("realm") != "rancho" or realm.get("loginTheme") != "rancho":
        _fallo(f"realm/theme inesperado: {realm.get('realm')} / {realm.get('loginTheme')}")
    print("realm rancho con loginTheme=rancho", flush=True)

    raweb = _cliente("raweb")
    raapi = _cliente("raapi")
    ra_mcp = _cliente("ra-mcp")
    if not raweb.get("publicClient") or raweb.get("directAccessGrantsEnabled") or raweb.get("implicitFlowEnabled"):
        _fallo("raweb no quedó como cliente público sin DAG ni implicit")
    if raapi.get("standardFlowEnabled") or raapi.get("directAccessGrantsEnabled"):
        _fallo("raapi tiene flujos interactivos")
    if ra_mcp.get("publicClient") or not ra_mcp.get("standardFlowEnabled") or ra_mcp.get("directAccessGrantsEnabled"):
        _fallo("ra-mcp no quedó confidencial con solo standard flow")
    atributos = ra_mcp.get("attributes") or {}
    if atributos.get("standard.token.exchange.enabled") != "true":
        _fallo("ra-mcp no tiene Standard Token Exchange habilitado")
    print("clientes raweb, raapi y ra-mcp verificados")

    _, serverinfo = _admin_json("GET", f"{PUBLIC}/admin/serverinfo")
    features = {item.get("name"): item.get("enabled") for item in (serverinfo.get("features") or [])}
    if features.get("token-exchange") is True:
        _fallo("Legacy Token Exchange V1 está habilitado")
    print("Legacy Token Exchange V1 no está habilitado")

    consulta = urllib.parse.urlencode({"username": DEMO_USER, "exact": "true"})
    _, usuarios = _admin_json("GET", f"{PUBLIC}/admin/realms/rancho/users?{consulta}")
    if not usuarios:
        _fallo("usuario DEV ausente")
    user_id = usuarios[0]["id"]
    _, asignados = _admin_json(
        "GET",
        f"{PUBLIC}/admin/realms/rancho/users/{user_id}/role-mappings/clients/{raapi['id']}",
    )
    nombres = {rol.get("name") for rol in asignados}
    if not {"clientes:read", "pedidos:write"} <= nombres:
        _fallo(f"roles DEV incompletos: {sorted(nombres)}")
    print("usuario DEV con clientes:read y pedidos:write")

    _, ejemplo = _admin_json(
        "GET",
        f"{PUBLIC}/admin/realms/rancho/clients/{raweb['id']}/evaluate-scopes/generate-example-access-token?scope=openid&userId={user_id}",
    )
    if not _aud_incluye(ejemplo, "raapi"):
        _fallo(f"evaluate raweb sin aud raapi: {ejemplo.get('aud')}")
    roles_ejemplo = set(_roles(ejemplo))
    if not {"clientes:read", "pedidos:write"} <= roles_ejemplo:
        _fallo(f"evaluate raweb sin roles: {sorted(roles_ejemplo)}")
    if ejemplo.get("azp") not in (None, "raweb") and ejemplo.get("issuedFor") not in (None, "raweb"):
        pass
    print("evaluate raweb: aud incluye raapi y roles del usuario DEV")

    web = _token_authorization_code("raweb", "http://localhost:8080/")
    web_claims = _claims(web["access_token"])
    print("TOKEN raweb")
    print(json.dumps(_resumen(web_claims, "access token Keycloak de raweb"), indent=2, ensure_ascii=False))
    if web_claims.get("azp") != "raweb" or not _aud_incluye(web_claims, "raapi"):
        _fallo("el access token real de raweb no tiene azp=raweb y aud=raapi")
    if "ra-mcp" in _como_lista(web_claims.get("aud")):
        _fallo("el token de raweb no debe incluir la audiencia ra-mcp")
    if not {"clientes:read", "pedidos:write"} <= set(_roles(web_claims)):
        _fallo(f"roles reales de raweb: {_roles(web_claims)}")

    mcp = _token_authorization_code("ra-mcp", "http://localhost:8000/auth/callback", CLIENT_SECRET)
    mcp_claims = _claims(mcp["access_token"])
    print("TOKEN upstream ra-mcp")
    print(json.dumps(_resumen(mcp_claims, "access token Keycloak emitido para ra-mcp"), indent=2, ensure_ascii=False))
    if mcp_claims.get("azp") != "ra-mcp" or not _aud_incluye(mcp_claims, "ra-mcp"):
        _fallo(f"el token upstream de ra-mcp no tiene azp/aud ra-mcp: azp={mcp_claims.get('azp')} aud={mcp_claims.get('aud')}")

    _, exchanged = _json(
        "POST",
        f"{ISSUER}/protocol/openid-connect/token",
        form={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "client_id": "ra-mcp",
            "client_secret": CLIENT_SECRET,
            "subject_token": mcp["access_token"],
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": "raapi",
        },
    )
    down = _claims(exchanged["access_token"])
    print("TOKEN downstream Token Exchange")
    print(json.dumps(_resumen(down, "access token intercambiado para raapi"), indent=2, ensure_ascii=False))
    if not _aud_incluye(down, "raapi"):
        _fallo(f"token exchange sin aud raapi: {down.get('aud')}")
    if "ra-mcp" in _como_lista(down.get("aud")):
        _fallo("el token downstream todavía incluye aud ra-mcp")
    if down.get("sub") != mcp_claims.get("sub"):
        _fallo("el token exchange no conservó sub")
    if down.get("preferred_username") != DEMO_USER:
        _fallo("el token exchange no conservó preferred_username")
    if set(_roles(down)) != {"clientes:read", "pedidos:write"} and not {"clientes:read", "pedidos:write"} <= set(_roles(down)):
        _fallo(f"roles downstream inesperados: {_roles(down)}")
    print("Token Exchange V2 emitió un token con aud=raapi y el mismo usuario")


def _como_lista(aud) -> list:
    if aud is None:
        return []
    if isinstance(aud, list):
        return aud
    return [aud]


def _resumen(claims: dict, tipo: str) -> dict:
    return {
        "tipo": tipo,
        "iss": claims.get("iss"),
        "azp": claims.get("azp"),
        "aud": claims.get("aud"),
        "sub": claims.get("sub"),
        "preferred_username": claims.get("preferred_username"),
        "email": claims.get("email"),
        "resource_access": claims.get("resource_access"),
        "scope": claims.get("scope"),
    }


if __name__ == "__main__":
    main()
