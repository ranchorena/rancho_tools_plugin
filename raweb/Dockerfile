# Usar una imagen base de Node.js
FROM node:18-alpine as builder

# Establecer el directorio de trabajo
WORKDIR /app

# Argumentos de build que pueden ser pasados desde docker-compose
ARG API_URL
ARG GEOSERVER_URL

# Establecer las variables de entorno para que estén disponibles durante el build
ENV API_URL=${API_URL}
ENV GEOSERVER_URL=${GEOSERVER_URL}

# Copiar los archivos de la aplicación Raweb
COPY package*.json ./
COPY rollup.config.js ./
# COPY svelte.config.js ./ # Archivo no encontrado en el proyecto, comentado/eliminado
COPY public public/
COPY src src/
COPY scripts scripts/

# Instalar las dependencias
RUN npm install

# Construir la aplicación
RUN npm run build

# Etapa de producción
FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/public /app/public
COPY package*.json ./
# COPY rollup.config.js ./ # Comentado: rollup.config.js no es necesario para servir con sirv en producción

# Instalar dependencias de producción (sirv-cli)
RUN npm install --omit=dev

# Exponer el puerto 8080 (puerto por defecto de sirv)
EXPOSE 8080

# Comando para iniciar la aplicación
CMD [ "npm", "run", "start" ]
