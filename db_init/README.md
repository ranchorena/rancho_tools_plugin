# PostgreSQL de negocio

Hay dos modos. No se reemplaza la base del host por el contenedor `db`.

## DEV habitual

La base de referencia es la PostgreSQL que ya corre en el host, puerto **5432**.
Contiene los datos vigentes. Keycloak sigue en su propio `keycloak-db` de Docker
y no usa esta base.

ra-ng-api en Windows (también puede leer `ra-ng-api/.env`):

```text
DB_HOST=localhost
DB_PORT=5432
```

Si `localhost` resolviera solo a `::1` y la conexión fallara, el valor de
trabajo es `127.0.0.1` en el mismo puerto.

ra-ng-api dentro de Docker Desktop:

```text
DB_HOST=host.docker.internal
DB_PORT=5432
```

`DB_USER`, `DB_PASSWORD`, `DB_NAME` y `DB_SCHEMA` salen de las mismas variables
en los dos casos. `DB_SCHEMA` por defecto es `generalbelgrano`.

Fuera de Docker, `ra-ng-api` completa con `ra-ng-api/.env` las variables que el proceso no trae. El contenedor
no debe heredar `DB_HOST=localhost`: dentro de la red de Docker ese nombre es
el propio contenedor. Compose usa `DB_HOST_DOCKER` y `DB_PORT_DOCKER`.

```powershell
docker compose up -d ra-ng-api
```

Ese comando no levanta el servicio `db`.

## Standalone

Para un servidor nuevo, otra notebook, recuperación, CI o una instalación
completa. El servicio `db` está en el perfil `standalone`.

```powershell
$env:DB_HOST_DOCKER = "db"
$env:DB_PORT_DOCKER = "5432"
docker compose --profile standalone up -d db ra-ng-api
```

Dentro de la red, ra-ng-api usa `DB_HOST=db` y el puerto 5432 del contenedor.
Desde Windows, ese PostgreSQL queda publicado en el puerto **5433** para no
pisar el 5432 del host.

`db_init/restore_dump.sh` se monta en `/docker-entrypoint-initdb.d` y restaura
`generalbelgrano-20261117.dump` solo cuando el volumen `postgres_data` está
vacío. No borrar ese volumen para reintentar la carga. Un volumen inicializado
con otra versión mayor de PostgreSQL no sirve para esta imagen: hay que usar
un volumen nuevo.

## Dump y versión

`generalbelgrano-20261117.dump` es la fuente de la instalación standalone.
Salió del host con `pg_dump` 16.2.

| Dato | Valor |
| --- | --- |
| Base original | PostgreSQL 16.2, PostGIS 3.4 |
| Dump | `pg_dump` 16.2, archive custom 1.15 |
| Imagen de `db` | `postgis/postgis:16-3.4-alpine` (PostgreSQL 16.4, PostGIS 3.4.3) |

La imagen crea la extensión PostGIS en `10_postgis.sh` antes de
`restore_dump.sh`. Para regenerar el dump, usar el `pg_dump` de PostgreSQL 16,
no un cliente 17: el archive 1.16 no lo abre el `pg_restore` de esta imagen.

`generalbelgrano-20261014.dump` quedó de un `pg_dump` 17 (archive 1.16) y este
servicio no lo monta.
