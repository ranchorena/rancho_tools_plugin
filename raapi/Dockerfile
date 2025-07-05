# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos e instalarlos
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación
COPY . .

# Exponer el puerto 5000 (puerto por defecto de Flask)
EXPOSE 5000

# Variables de entorno para la base de datos (serán sobrescritas por docker-compose si se usa)
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_HOST=db # Asumiendo que el servicio de la BD se llamará 'db' en docker-compose
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para iniciar la aplicación Flask
CMD ["flask", "run"]
