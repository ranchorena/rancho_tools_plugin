#!/bin/sh
# Perfil Compose "standalone", solo en un volumen vacío.
# generalbelgrano-20261014.dump es archive 1.16 (pg_dump 17, origen PostgreSQL 16.2).
# postgres:13-alpine no puede restaurarlo. Ver README.md de esta carpeta.
set -e

echo "Restaurando generalbelgrano-20261014.dump a la base de datos '$POSTGRES_DB' con el usuario '$POSTGRES_USER'..."

# El entrypoint de postgres ya crea la base de datos $POSTGRES_DB.
# El dump fue creado desde la base de datos 'postgres' para el esquema 'generalbelgrano'.
# Se asume que POSTGRES_DB en el entorno es 'postgres' (o la base de datos destino correcta).
# y POSTGRES_USER es 'postgres' (o el usuario correcto con permisos).

# Crear el esquema 'generalbelgrano' si no existe
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "CREATE SCHEMA IF NOT EXISTS generalbelgrano;"

pg_restore --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --verbose --no-owner --no-privileges --schema="generalbelgrano" /docker-entrypoint-initdb.d/generalbelgrano-20261014.dump

echo "Restauración de generalbelgrano-20261014.dump completada."
