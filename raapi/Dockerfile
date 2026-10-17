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

# DEV habitual dentro de Docker Desktop: la PostgreSQL del host.
# El perfil standalone de Compose sobreescribe DB_HOST=db.

ENV DB_HOST=DB_HOST_DOCKER

ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para iniciar la aplicación Flask
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
CMD ["flask", "run"]
