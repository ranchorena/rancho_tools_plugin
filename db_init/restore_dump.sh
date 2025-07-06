#!/bin/sh
set -e

echo "Restaurando generalbelgrano.dump a la base de datos '$POSTGRES_DB' con el usuario '$POSTGRES_USER'..."

# El entrypoint de postgres ya crea la base de datos $POSTGRES_DB.
# El dump fue creado desde la base de datos 'postgres' para el esquema 'generalbelgrano'.
# Se asume que POSTGRES_DB en el entorno es 'postgres' (o la base de datos destino correcta).
# y POSTGRES_USER es 'postgres' (o el usuario correcto con permisos).

pg_restore --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --verbose --no-owner --no-privileges --schema="generalbelgrano" /docker-entrypoint-initdb.d/generalbelgrano.dump

echo "Restauración de generalbelgrano.dump completada."
