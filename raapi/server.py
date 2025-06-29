# server.py
# coding=utf-8

from flask import Flask, request, jsonify
from markupsafe import escape
import json, requests
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

from config import Session, jwt_key as app_jwt_key # Renombrado para evitar conflicto de nombres
from datetime import datetime
from flask_cors import CORS
from flasgger import Swagger
from sqlalchemy import text # Para ejecutar SQL directamente si es necesario

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = app_jwt_key # Usar la clave importada
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 6 # 6 horas
jwt = JWTManager(app)
CORS(app)

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
    # Configuración del título, versión y OpenAPI
    "openapi": "3.0.0",  # Versión de OpenAPI
    "info": {
        "title": "RAApi",    # Título personalizado
        "version": "3.0.1",    # Versión personalizada
        # "description": "RA API"  # Opcional
    }
}

Swagger(app, config=swagger_config)  # Aplica la configuración

@app.route("/")
def root():
    return "<h1>Server is running</h1>"

import re # Para parsear la dirección

# Función para parsear la dirección (simple)
def parse_direccion(direccion_str):
    # Intenta encontrar un número al final de la cadena, precedido opcionalmente por espacios.
    # El resto será considerado el nombre de la calle.
    match = re.match(r"^(.*?)\s*(\d+)\s*$", direccion_str.strip())
    if match:
        calle = match.group(1).strip().upper() # Convertir a mayúsculas para comparar
        try:
            altura = int(match.group(2))
            return calle, altura
        except ValueError:
            return None, None # No es un número válido
    # Si no hay número, podría ser solo el nombre de la calle (sin altura)
    # o un formato no esperado. Por ahora, si no hay número, no lo manejamos específicamente.
    # Podríamos buscar la calle sin altura, pero la lógica se complica.
    # Para este caso, si no hay altura, devolvemos la dirección completa como calle.
    # Esto requeriría que la búsqueda SQL maneje el caso de altura NULL o no filtrar por altura.
    # Por ahora, requerimos una altura.
    return None, None


@app.route("/buscar_direccion", methods=["POST"])
def buscar_direccion():
    """
    Busca una dirección (calle y altura) y devuelve el punto medio del tramo correspondiente.
    El punto medio se calcula como el centroide de la geometría del tramo, transformado a EPSG:4326 (lat/lon).
    ---
    tags:
      - Direcciones
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              direccion:
                type: string
                description: La dirección a buscar (ej. "SAN MARTIN 123").
                example: "SARMIENTO 550"
    responses:
      200:
        description: Coordenadas del punto medio del tramo en EPSG:4326.
        schema:
          type: object
          properties:
            latitud:
              type: number
              format: float
            longitud:
              type: number
              format: float
            tramo_info:
              type: object
              properties:
                id:
                  type: integer
                nombre_calle:
                  type: string
                desde:
                  type: integer
                hasta:
                  type: integer
      400:
        description: Error en la solicitud (ej. dirección no proporcionada o formato incorrecto).
      404:
        description: Dirección no encontrada o altura fuera de rango para la calle especificada.
      500:
        description: Error interno del servidor.
    """
    data = request.get_json()
    if not data or "direccion" not in data:
        return jsonify({"error": "La dirección es requerida"}), 400

    direccion_completa = data["direccion"]
    nombre_calle, altura = parse_direccion(direccion_completa)

    if not nombre_calle or altura is None:
        return jsonify({"error": "Formato de dirección incorrecto. Se espera 'Nombre de Calle Número' (ej. SARMIENTO 550)."}), 400

    session = Session()
    try:
        # Usamos ST_Centroid para obtener el punto medio y ST_Transform para convertir a EPSG:4326 (lat/lon)
        # La función ST_AsGeoJSON se usa para extraer las coordenadas del punto.
        # Asegúrate de que PostGIS esté habilitado en tu base de datos (CREATE EXTENSION postgis;)
        # El SRID original es 5347 según el DDL.
        # La búsqueda de calle es case-insensitive usando UPPER() en ambos lados.
        query = text("""
            SELECT
                id,
                calle,
                desde,
                hasta,
                ST_AsGeoJSON(ST_Transform(ST_Centroid(geometry), 4326)) as centroide_geojson
            FROM
                generalbelgrano.tramos
            WHERE
                UPPER(calle) = UPPER(:nombre_calle)
                AND :altura BETWEEN desde AND hasta
            LIMIT 1;
        """)

        result = session.execute(query, {"nombre_calle": nombre_calle, "altura": altura}).fetchone()

        if result:
            tramo_id, tramo_calle, tramo_desde, tramo_hasta, centroide_geojson_str = result

            if centroide_geojson_str:
                centroide_geojson = json.loads(centroide_geojson_str)
                # GeoJSON para un Point tiene las coordenadas en formato [longitud, latitud]
                longitud, latitud = centroide_geojson['coordinates']

                return jsonify({
                    "latitud": latitud,
                    "longitud": longitud,
                    "tramo_info": {
                        "id": tramo_id,
                        "nombre_calle": tramo_calle,
                        "desde": tramo_desde,
                        "hasta": tramo_hasta
                    }
                }), 200
            else:
                # Esto no debería pasar si la geometría existe y ST_Centroid funciona.
                return jsonify({"error": "No se pudo calcular el centroide para el tramo encontrado."}), 500
        else:
            # Podríamos dar un mensaje más específico si la calle existe pero la altura no.
            # Para ello, haríamos una primera consulta por la calle y luego verificaríamos la altura.
            # Por ahora, un 404 general es suficiente.
            return jsonify({"error": f"Dirección no encontrada: Calle '{nombre_calle}' con altura {altura} no existe o altura fuera de rango."}), 404

    except Exception as e:
        # Loggear el error es importante para depuración
        app.logger.error(f"Error en /buscar_direccion: {e}")
        app.logger.error(f"SQL Query Parameters: nombre_calle='{nombre_calle}', altura={altura}")
        return jsonify({"error": "Error interno del servidor al procesar la búsqueda."}), 500
    finally:
        session.close()


# --- Nuevos Endpoints para Clientes ---
from API import API # Importar la clase/módulo con la lógica de BD

@app.route("/api/clientes/buscar", methods=["POST"])
# @jwt_required() # Descomentar si se necesita protección JWT
def buscar_clientes_api():
    """
    Busca clientes por nombre, dirección, o calle/altura.
    ---
    tags:
      - Clientes
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              criterio:
                type: string
                description: "Criterio de búsqueda: 'nombre', 'direccion', o 'calle_altura'"
                example: "nombre"
              nombre_cliente:
                type: string
                description: "Nombre del cliente a buscar (si criterio es 'nombre')"
                example: "Juan Perez"
              direccion:
                type: string
                description: "Dirección a buscar (si criterio es 'direccion')"
                example: "Av. Siempreviva 742"
              calle:
                type: string
                description: "Nombre de la calle (si criterio es 'calle_altura')"
                example: "SARMIENTO"
              altura:
                type: string # Se recibe como string, API.py lo convierte a int si es necesario
                description: "Altura de la calle (opcional, si criterio es 'calle_altura')"
                example: "550"
    responses:
      200:
        description: Lista de clientes encontrados.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  nombre:
                    type: string
                  direccion:
                    type: string
                  calle:
                    type: string
                  altura:
                    type: integer
      400:
        description: Parámetros inválidos o faltantes.
      500:
        description: Error interno del servidor.
    """
    data = request.get_json()
    if not data or "criterio" not in data:
        return jsonify({"error": "El campo 'criterio' es requerido"}), 400

    criterio = data.get("criterio")
    session = Session()
    try:
        clientes_encontrados = []
        if criterio == "nombre":
            nombre = data.get("nombre_cliente")
            if not nombre:
                return jsonify({"error": "El campo 'nombre_cliente' es requerido para el criterio 'nombre'"}), 400
            clientes_encontrados = API.buscar_cliente_por_nombre(session, nombre)
        elif criterio == "direccion":
            direccion_b = data.get("direccion")
            if not direccion_b:
                return jsonify({"error": "El campo 'direccion' es requerido para el criterio 'direccion'"}), 400
            clientes_encontrados = API.buscar_clientes_por_direccion(session, direccion_b)
        elif criterio == "calle_altura":
            calle_b = data.get("calle")
            if not calle_b: # La calle es requerida para este criterio
                return jsonify({"error": "El campo 'calle' es requerido para el criterio 'calle_altura'"}), 400
            altura_b = data.get("altura") # Altura es opcional
            clientes_encontrados = API.buscar_clientes_por_calle_altura(session, calle_b, altura_b)
        else:
            return jsonify({"error": f"Criterio '{criterio}' no válido. Use 'nombre', 'direccion' o 'calle_altura'."}), 400

        return jsonify(clientes_encontrados), 200

    except Exception as e:
        app.logger.error(f"Error en /api/clientes/buscar: {e}")
        return jsonify({"error": "Error interno del servidor al buscar clientes."}), 500
    finally:
        session.close()

@app.route("/api/clientes/actualizar/<int:cliente_id>", methods=["PUT"])
# @jwt_required() # Descomentar si se necesita protección JWT
def actualizar_cliente_api(cliente_id):
    """
    Actualiza los datos de un cliente existente.
    ---
    tags:
      - Clientes
    parameters:
      - name: cliente_id
        in: path
        required: true
        description: ID del cliente a actualizar.
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              docenas:
                type: number
                format: float
                nullable: true
              nro_pao:
                type: integer
                nullable: true
              tiene_pedido:
                type: boolean # En JSON es true/false, API.py lo convierte a 1/0
                nullable: true
              es_regalo:
                type: boolean # En JSON es true/false, API.py lo convierte a 1/0
                nullable: true
              observaciones:
                type: string
                nullable: true
              horario:
                type: string
                format: time # HH:MM:SS
                nullable: true
                example: "10:30:00"
    responses:
      200:
        description: Cliente actualizado con éxito.
        content:
          application/json:
            schema:
              type: object
              properties:
                mensaje:
                  type: string
                  example: "Cliente actualizado correctamente."
      400:
        description: Datos de entrada inválidos.
      404:
        description: Cliente no encontrado.
      500:
        description: Error interno del servidor.
    """
    datos_actualizados = request.get_json()
    if not datos_actualizados:
        return jsonify({"error": "No se proporcionaron datos para actualizar."}), 400

    # Validación básica de tipos (más robusta podría hacerse con Marshmallow o Pydantic)
    allowed_fields = {"docenas", "nro_pao", "tiene_pedido", "es_regalo", "observaciones", "horario"}
    # Filtrar solo los campos permitidos para evitar inyección de campos no deseados
    datos_filtrados = {k: v for k, v in datos_actualizados.items() if k in allowed_fields}

    if not datos_filtrados:
         return jsonify({"error": "No se proporcionaron campos válidos para actualizar."}), 400

    session = Session()
    try:
        # La función API.actualizar_cliente maneja el commit/rollback internamente
        actualizacion_exitosa = API.actualizar_cliente(session, cliente_id, datos_filtrados)

        if actualizacion_exitosa:
            return jsonify({"mensaje": "Cliente actualizado correctamente."}), 200
        else:
            # Podría ser que el cliente no exista (rowcount = 0) o un error en la BBDD.
            # Para diferenciar, API.actualizar_cliente debería ser más explícito o
            # podríamos hacer una verificación previa de existencia del cliente aquí.
            # Por ahora, si devuelve False, asumimos que no se encontró o no se pudo actualizar.
            # Chequeamos si el cliente existe para dar un 404 más preciso.
            cliente_existe_query = text("SELECT 1 FROM generalbelgrano.clientes WHERE id = :id")
            existe = session.execute(cliente_existe_query, {"id": cliente_id}).fetchone()
            if not existe:
                return jsonify({"error": f"Cliente con ID {cliente_id} no encontrado."}), 404
            else: # Existe pero no se actualizó, podría ser un error interno o datos sin cambios reales
                return jsonify({"error": "No se pudo actualizar el cliente. Verifique los datos o inténtelo más tarde."}), 500


    except Exception as e:
        session.rollback() # Asegurar rollback si la excepción ocurre aquí y no en API
        app.logger.error(f"Error en /api/clientes/actualizar/{cliente_id}: {e}")
        return jsonify({"error": "Error interno del servidor al actualizar el cliente."}), 500
    finally:
        session.close()

if __name__ == '__main__':
    # Habilitar logging para ver errores de Flask y SQLAlchemy
    import logging
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler() # Log to stderr
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000, debug=True)
