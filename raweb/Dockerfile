# Usar una imagen base de Node.js
FROM node:18-alpine as builder

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación Raweb
COPY package*.json ./
COPY rollup.config.js ./
COPY svelte.config.js ./
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
COPY rollup.config.js ./ # Necesario para sirv

# Instalar dependencias de producción (sirv-cli)
RUN npm install --omit=dev

# Exponer el puerto 8080 (puerto por defecto de sirv)
EXPOSE 8080

# Comando para iniciar la aplicación
CMD [ "npm", "run", "start" ]
