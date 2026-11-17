#!/bin/sh
# Perfil Compose "standalone", solo en un volumen vacío.
# generalbelgrano-20261117.dump es archive 1.15 (pg_dump 16.2, origen PostgreSQL 16.2, PostGIS 3.4).
# postgis/postgis:16-3.4-alpine ejecuta antes 10_postgis.sh y deja creada la extensión.
set -e

echo "Restaurando generalbelgrano-20261117.dump a la base de datos '$POSTGRES_DB' con el usuario '$POSTGRES_USER'..."

# El entrypoint de postgres ya crea la base de datos $POSTGRES_DB.
# El dump incluye el esquema generalbelgrano. 10_postgis.sh ya creó la extensión.

pg_restore --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --verbose --no-owner --no-privileges --schema="generalbelgrano" /docker-entrypoint-initdb.d/generalbelgrano-20261117.dump

echo "Restauración de generalbelgrano-20261117.dump completada."
