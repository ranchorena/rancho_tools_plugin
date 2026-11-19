# docker image rm k8sgeosystems/geoserver:latest
# docker build -t k8sgeosystems/geoserver:latest --no-cache /usr/src/app/geoserver
# docker push k8sgeosystems/geoserver:latest


# docker run -d --restart=always -p 8087:8080 --name geoserver-test -v C:\docker\volumes\geoserver_data:/opt/geoserver_data k8sgeosystems/geoserver:latest

# Si tuviera que levantar geoserver para uat de fibergis
# docker run -d --restart=always -p 8082:8080 -v /home/geouser/volume-uat/geoserver_data:/opt/geoserver_data --name fggeoserver-uat k8sgeosystems/geoserver:latest

---
# En mi pc para probar oauth2 hice 
# docker build -t k8sgeosystems/geoserver:2.26.2 .
# docker run -d --restart=always -p 8088:8080 --name geoserver-oauth2 -v /c/docker/volumes/geoserver_data_oauth2:/opt/geoserver_data k8sgeosystems/geoserver:2.26.2

# En 192.168.1.91 - geoserver-oauth2 - Investigacion GeoServer con openid oauth2
# docker run -d --restart=always -p 8088:8080 --name geoserver-oauth2 -v /home/geouser/volume-qa/geoserver-data-oauth2:/opt/geoserver_data k8sgeosystems/geoserver:2.26.2

# Para CABA
# docker run -d --restart=always -p 8787:8080 --name gcba-geoserver-qa -v /home/geouser/volume-qa/caba/geoserver-data:/opt/geoserver_data k8sgeosystems/geoserver:2.26.2

# http://192.168.1.91:8787/geoserver/web/

---
# Imagen local, una sola vez por máquina. Compose no la construye ni la descarga.
# docker build -t k8sgeosystems/rageoserver:2.26.2 .

# El data dir es GEOSERVER_DATA_DIR del .env de la raíz (en esta PC, /c/docker/volumes/geoserver_data).
# Si rageoserver-qa ya existe por un docker run, pararlo y borrarlo antes. No borrar el data dir.
# docker compose --profile geoserver up -d geoserver

# Con el directorio vacío, el primer arranque genera la clave de cifrado de ese servidor.
# Copiar a mano rageoserver/workspaces/GeneralBelgrano dentro de workspaces/ del data dir.
# En la UI, guardar el datastore: host.docker.internal:5432 con la PostgreSQL del host,
# o db:5432 si la base es la del perfil standalone. Ahí se cifra la clave con la de este servidor.
# Los arranques siguientes reutilizan el volumen. No montar el workspace del repo como data dir.
