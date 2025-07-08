FROM docker.osgeo.org/geoserver:2.26.2 as geoserver

# Puerto default de Tomcat. Cambiar en caso de exponerlo por medio de un Proxy
EXPOSE 8080

ENV TMPDIR=/var/tmp
RUN mkdir -p /var/tmp && chmod 1777 /var/tmp

# Instalación de utilidades necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sudo \
    nano \
    vim \
    locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Generar el locale es_ES.UTF-8
    sed -i '/es_ES.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen es_ES.UTF-8

# Configurar las variables de entorno para usar es_ES.UTF-8 por defecto
ENV LANG=es_ES.UTF-8 \
    LC_ALL=es_ES.UTF-8

# # Crear el usuario tomcat
# RUN groupadd -r tomcat && \
#     useradd -r -g tomcat -d /opt/apache-tomcat-9.0.86 -s /bin/false tomcat
# # Cambiar el usuario y grupo del directorio /opt/geoserver_data a tomcat:tomcat
# RUN chown -R tomcat:tomcat /opt/geoserver_data
# # Cambiar los permisos de la carpeta /opt/geoserver_data/workspaces y su contenido a 755
# # RUN chmod -R 755 /opt/geoserver_data/workspaces

# Crear el grupo geouser y el usuario geouser
# RUN groupadd -r geouser && \
#     useradd -r -g geouser -d /opt/geoserver_data -s /bin/false geouser

# # Cambiar el propietario de todos los archivos relacionados con GeoServer a geouser:geouser
# RUN chown -R geouser:geouser /opt/geoserver_data && \
#     chmod -R 755 /opt/geoserver_data

#/opt/apache-tomcat-9.0.86/webapps/geoserver/WEB-INF/lib/
# Copia de Drivers JDBC de Oracle
COPY data/driver/*.jar /usr/local/tomcat/webapps/geoserver/WEB-INF/lib/
COPY data/web.xml /usr/local/tomcat/webapps/geoserver/WEB-INF/
COPY data/epsg.properties /opt/geoserver_data/user_projections/
# COPY data/security/* /opt/geoserver_data/security/

# Cambiar al usuario geouser para ejecutar GeoServer
# USER geouser

