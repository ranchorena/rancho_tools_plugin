# Utilizar la imagen oficial de Nginx como base
FROM nginx

# Copiar la configuración del proxy reverso a la ubicación en el contenedor
# COPY nginx.conf /etc/nginx/nginx.conf

# Eliminar el archivo de configuración predeterminado
# RUN rm /etc/nginx/conf.d/default.conf
# Eliminar todos los archivos de configuración existentes
RUN rm /etc/nginx/conf.d/*

# Copiar tu archivo de configuración del proxy reverso a la ubicación en el contenedor
# COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Exponer el puerto 80 para el tráfico entrante
EXPOSE 80

# Eliminar cualquier archivo o enlace simbólico existente en el directorio /var/log/nginx
RUN rm -f /var/log/nginx/access.log && \
    rm -f /var/log/nginx/error.log && \
    rm -f /var/log/nginx/access.log.1 && \
    rm -f /var/log/nginx/error.log.1

# Configuramos nginx para que genere un log de acceso
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Comando para iniciar Nginx cuando se inicie el contenedor
CMD ["nginx", "-g", "daemon off;"]