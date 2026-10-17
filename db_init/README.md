# PostgreSQL de negocio

Hay dos modos. No se reemplaza la base del host por el contenedor `db`.

## DEV habitual

La base de referencia es la PostgreSQL que ya corre en el host, puerto **5432**.
Contiene los datos vigentes. Keycloak sigue en su propio `keycloak-db` de Docker
y no usa esta base.

raapi en Windows:

```text
DB_HOST=localhost
DB_PORT=5432
```

Si `localhost` resolviera solo a `::1` y la conexión fallara, el valor de
trabajo es `127.0.0.1` en el mismo puerto.

raapi dentro de Docker Desktop:

```text
DB_HOST=host.docker.internal
DB_PORT=5432
```

`DB_USER`, `DB_PASSWORD`, `DB_NAME` y `DB_SCHEMA` salen de las mismas variables
en los dos casos. `DB_SCHEMA` por defecto es `generalbelgrano`.

El proceso de Windows lee el entorno del proceso, no `.env`. El contenedor
no debe heredar `DB_HOST=localhost`: dentro de la red de Docker ese nombre es
el propio contenedor. Compose usa `DB_HOST_DOCKER` y `DB_PORT_DOCKER`.

```powershell
docker compose up -d backend
```

Ese comando no levanta el servicio `db`.

## Standalone

Para un servidor nuevo, otra notebook, recuperación, CI o una instalación
completa. El servicio `db` está en el perfil `standalone`.

```powershell
$env:DB_HOST_DOCKER = "db"
$env:DB_PORT_DOCKER = "5432"
docker compose --profile standalone up -d db backend
```

Dentro de la red, raapi usa `DB_HOST=db` y el puerto 5432 del contenedor.
Desde Windows, ese PostgreSQL queda publicado en el puerto **5433** para no
pisar el 5432 del host.

`db_init/restore_dump.sh` se monta en `/docker-entrypoint-initdb.d` y restaura
`generalbelgrano-20261014.dump` solo cuando el volumen `postgres_data` está
vacío. No borrar ese volumen para reintentar la carga.

## Dump y versión

No modificar `generalbelgrano-20261014.dump`. Es la fuente de una instalación
limpia futura.

| Dato | Valor |
| --- | --- |
| Base original | PostgreSQL 16.2 |
| Dump | `pg_dump` 17.0, archive custom 1.16 |
| Imagen actual de `db` | `postgres:13-alpine` |

`postgres:13` no restaura un archive 1.16. Esa incompatibilidad no afecta al
DEV habitual, que no usa este contenedor.

La dirección para dejar usable la instalación standalone, en una tarea aparte,
es alinear la imagen Docker con PostgreSQL 16 y generar o restaurar dumps
compatibles con esa versión. Hasta entonces el script de restore no completa
la carga sobre `postgres:13-alpine`.
