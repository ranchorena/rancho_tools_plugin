# Keycloak DEV — realm rancho

Keycloak **26.8.1** es el identity provider de `raweb`, `raapi` y `ra-mcp`.
`start-dev` en este Compose es solo para la máquina local. Un ambiente real
usa `start`, HTTPS y un reverse proxy, sin usuario demo y sin este bootstrap.

La base de Keycloak es el servicio `keycloak-db` (`postgres:16-alpine`,
volumen `keycloak_db_data`). No comparte volumen ni schema con la PostgreSQL
de negocio. En DEV habitual esa base es la del host (`localhost:5432`). El
servicio Compose `db` solo entra con el perfil `standalone`.

## Fronteras de audiencia

Comprobado con Authorization Code + PKCE y Standard Token Exchange V2
contra Keycloak 26.8.1. El usuario DEV `rancho` tiene ambos client roles.

```text
Token recibido por el flujo de raweb
issuer:  http://localhost:8081/realms/rancho
azp:     raweb
aud:     raapi
tipo:    access token Keycloak
resource_access.raapi.roles: clientes:read, pedidos:write
sub y preferred_username: el usuario rancho

Token recibido/procesado por ra-mcp (upstream, lo valida JWTVerifier)
issuer:  http://localhost:8081/realms/rancho
azp:     ra-mcp
aud:     ra-mcp y raapi
tipo:    access token Keycloak del Authorization Code
resource_access.raapi.roles: clientes:read, pedidos:write

JWT interno de FastMCP (lo presenta Cursor a /mcp)
issuer:  http://localhost:8000
aud:     http://localhost:8000/mcp
tipo:    JWT firmado por RA_MCP_JWT_SIGNING_KEY
         No se envía a raapi.

Token intercambiado enviado a raapi
issuer:  http://localhost:8081/realms/rancho
azp:     ra-mcp
aud:     raapi
tipo:    access token de Standard Token Exchange V2
resource_access.raapi.roles: clientes:read, pedidos:write
sub y preferred_username: los mismos del usuario original
```

`audience=raapi` en el Token Exchange solo filtra audiencias que el cliente
`ra-mcp` ya puede emitir (client scope `raapi-audience`). No crea la audiencia.
Legacy Token Exchange V1 no se habilita.

Los permisos son client roles de `raapi`: `clientes:read` y `pedidos:write`.
No hay un segundo sistema de scopes OAuth con los mismos nombres.

## Variables

Copiar los nombres desde el `.env.example` de la raíz al `.env` local
(ignorado por Git). `RANCHO_DEMO_PASSWORD=rancho-demo` es una credencial
descartable de esta máquina, no una clave productiva. El resto de secrets
son valores locales que no se versionan.

## Levantar

```powershell
docker compose up -d keycloak-db keycloak keycloak-bootstrap
docker logs rancho-keycloak-bootstrap
python infra/keycloak/verify_dev.py
```

`verify_dev.py` lee el `.env` si las variables ya están en el proceso.
Comprueba discovery, JWKS, clientes, theme, usuario DEV, el access token
real de `raweb` (Authorization Code + PKCE, sin Direct Access Grant) y el
Token Exchange V2.

El claim `iss` es siempre `http://localhost:8081/realms/rancho`.
`KEYCLOAK_JWKS_URL` en el host es
`http://127.0.0.1:8081/realms/rancho/protocol/openid-connect/certs`.
El contenedor `backend` no reutiliza esa variable: usa
`KEYCLOAK_JWKS_URL_DOCKER`
(`http://keycloak:8080/realms/rancho/protocol/openid-connect/certs`).
`fullScopeAllowed`, los client scopes, los audience mappers y los scope
mappings de `raweb` y `ra-mcp` salen de `rancho-realm.json`. El bootstrap
no los reescribe: solo fija el secret de `ra-mcp`, el usuario DEV y sus
role mappings.

## URLs locales

```text
Keycloak:          http://localhost:8081
Admin:             http://localhost:8081/admin
Realm:             http://localhost:8081/realms/rancho
OIDC discovery:    http://localhost:8081/realms/rancho/.well-known/openid-configuration
raweb:             http://localhost:8080
raapi:             http://localhost:5000
ra-mcp:            http://localhost:8000/mcp
```

Usuario DEV: `rancho` / `rancho-demo`.

## Importación

`--import-realm` carga `infra/keycloak/realm/rancho-realm.json` solo si el
realm no existe. No vuelve a pisar un realm ya importado. En
`clientScopeMappings` la clave es el cliente dueño de los roles (`raapi`)
y `client` es quien puede emitirlos (`raweb`, `ra-mcp`).

Para recrear DEV desde cero, sin tocar la base de negocio:

```powershell
docker compose stop keycloak keycloak-bootstrap keycloak-db
docker compose rm -f keycloak keycloak-bootstrap keycloak-db
docker volume rm rancho_tools_plugin_keycloak_db_data
docker compose up -d keycloak-db keycloak keycloak-bootstrap
```

## Clientes

| Cliente | Tipo | Uso |
| --- | --- | --- |
| `raweb` | público, PKCE S256 | Authorization Code desde el navegador |
| `raapi` | sin flujos interactivos | audiencia y roles |
| `ra-mcp` | confidencial | OAuthProxy y Token Exchange V2 |

Redirects DEV exactos: `http://localhost:8080/`, `http://localhost:8080/silent-check-sso.html` y `http://localhost:8000/auth/callback`.

El secret de `ra-mcp` lo escribe el bootstrap desde `KEYCLOAK_CLIENT_SECRET`.
No está en el JSON del realm.

## Theme

`loginTheme=rancho`, montado desde `infra/keycloak/themes/rancho`.

## Logs y detención

```powershell
docker logs rancho-keycloak
docker compose stop keycloak keycloak-bootstrap keycloak-db
```
