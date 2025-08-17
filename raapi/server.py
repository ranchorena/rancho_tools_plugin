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
# --- Nuevos Endpoints para Clientes ---
from API import API # Importar la clase/módulo con la lógica de BD

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = app_jwt_key # Usar la clave importada
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 6 # 6 horas
jwt = JWTManager(app)
CORS(app)

# Configuración simple de Swagger
swagger_config = {
    "headers": [],
    "specs": [{
        "endpoint": 'apispec',
        "route": '/apispec.json',
        "rule_filter": lambda rule: True,
        "model_filter": lambda tag: True,
    }],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
    "info": {
        "title": "RAApi",
        "version": "1.0.0",
        "description": "API para gestión de clientes y direcciones"
    }
}

Swagger(app, config=swagger_config)

@app.route("/")
def root():
    return "<h1>Server is running</h1>"

@app.route("/buscar_direccion", methods=["POST"])
def buscar_direccion():
    """
    Busca una dirección (calle y altura) y devuelve el punto medio del tramo correspondiente.
    ---
    tags:
      - Direcciones
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            direccion:
              type: string
              description: La dirección a buscar
              example: "SARMIENTO 550"
    responses:
      200:
        description: Coordenadas del punto medio del tramo
        schema:
          type: object
          properties:
            latitud:
              type: number
            longitud:
              type: number
            tramo_info:
              type: object
      400:
        description: Error en la solicitud
      404:
        description: Dirección no encontrada
      500:
        description: Error interno del servidor
    """
    data = request.get_json()
    if not data or "direccion" not in data:
        return jsonify({"error": "La dirección es requerida"}), 400

    direccion_completa = data["direccion"]

    with Session.begin() as session:
        try:
            resultado, datos = API.buscarDireccion(session, direccion_completa)
            
            if resultado == "success":
                return jsonify(datos), 200
            elif resultado == "invalid_format":
                return jsonify(datos), 400
            elif resultado == "not_found":
                return jsonify(datos), 404
            elif resultado == "geometry_error":
                return jsonify(datos), 500
            else:
                return jsonify({"error": "Error inesperado en la búsqueda."}), 500

        except Exception as e:
            app.logger.error(f"Error en /buscar_direccion: {e}")
            return jsonify({"error": "Error interno del servidor al procesar la búsqueda."}), 500


@app.route("/api/clientes/buscar", methods=["POST"])
# @jwt_required() # Descomentar si se necesita protección JWT
def buscar_clientes_api():
    """
    Busca clientes por nombre, dirección, o calle/altura.
    ---
    tags:
      - Clientes
    summary: Búsqueda de clientes
    description: |
      Permite buscar clientes utilizando diferentes criterios:
      - **nombre**: Busca por nombre del cliente (búsqueda parcial, insensible a mayúsculas)
      - **direccion**: Busca por dirección completa (búsqueda parcial, insensible a mayúsculas)
      - **calle_altura**: Busca por nombre de calle y opcionalmente altura específica
      
      Todos los resultados incluyen coordenadas geográficas en formato EPSG:4326 (WGS84).
    parameters:
      - name: body
        in: body
        required: true
        description: Parámetros de búsqueda según el criterio seleccionado
        schema:
          type: object
          required:
            - criterio
          properties:
            criterio:
              type: string
              enum: ["nombre", "direccion", "calle_altura"]
              description: "Criterio de búsqueda a utilizar"
              example: "nombre"
            nombre_cliente:
              type: string
              description: "Nombre del cliente a buscar (requerido para criterio 'nombre')"
              example: "Juan Pérez"
            direccion:
              type: string
              description: "Dirección a buscar (requerido para criterio 'direccion')"
              example: "San Martín 1250"
            calle:
              type: string
              description: "Nombre de la calle (requerido para criterio 'calle_altura')"
              example: "San Martín"
            altura:
              type: string
              description: "Altura de la calle (opcional para criterio 'calle_altura')"
              example: "1250"
          examples:
            buscar_por_nombre:
              summary: "Búsqueda por nombre"
              value:
                criterio: "nombre"
                nombre_cliente: "Juan"
            buscar_por_direccion:
              summary: "Búsqueda por dirección"
              value:
                criterio: "direccion"
                direccion: "San Martín"
            buscar_por_calle_altura:
              summary: "Búsqueda por calle y altura"
              value:
                criterio: "calle_altura"
                calle: "San Martín"
                altura: "1250"
    responses:
      200:
        description: Lista de clientes encontrados con coordenadas geográficas
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: "ID único del cliente"
                example: 123
              nombre:
                type: string
                description: "Nombre completo del cliente"
                example: "Juan Pérez"
              direccion:
                type: string
                description: "Dirección completa del cliente"
                example: "San Martín 1250"
              calle:
                type: string
                description: "Nombre de la calle"
                example: "San Martín"
              altura:
                type: integer
                description: "Altura de la calle"
                example: 1250
              longitud:
                type: number
                format: float
                description: "Longitud en grados decimales (EPSG:4326/WGS84)"
                example: -58.4173
              latitud:
                type: number
                format: float
                description: "Latitud en grados decimales (EPSG:4326/WGS84)"
                example: -34.6118
        examples:
          clientes_encontrados:
            summary: "Ejemplo de respuesta exitosa"
            value:
              - id: 123
                nombre: "Juan Pérez"
                direccion: "San Martín 1250"
                calle: "San Martín"
                altura: 1250
                longitud: -58.4173
                latitud: -34.6118
              - id: 456
                nombre: "María González"
                direccion: "San Martín 1340"
                calle: "San Martín"
                altura: 1340
                longitud: -58.4175
                latitud: -34.6120
      400:
        description: Parámetros inválidos o faltantes
        schema:
          type: object
          properties:
            error:
              type: string
              description: "Descripción del error"
        examples:
          criterio_faltante:
            summary: "Criterio faltante"
            value:
              error: "El campo 'criterio' es requerido"
          nombre_faltante:
            summary: "Nombre faltante"
            value:
              error: "El campo 'nombre_cliente' es requerido para el criterio 'nombre'"
          criterio_invalido:
            summary: "Criterio inválido"
            value:
              error: "Criterio 'invalido' no válido. Use 'nombre', 'direccion' o 'calle_altura'."
      500:
        description: Error interno del servidor
        schema:
          type: object
          properties:
            error:
              type: string
              description: "Descripción del error interno"
        examples:
          error_interno:
            summary: "Error de servidor"
            value:
              error: "Error interno del servidor al buscar clientes."
    """
    with Session.begin() as session:
      data = request.get_json()
      if not data or "criterio" not in data:
          return jsonify({"error": "El campo 'criterio' es requerido"}), 400

      criterio = data.get("criterio")
      # session = Session()
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
      # finally:
      #     session.close()

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
        description: ID del cliente a actualizar
        type: integer
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            docenas:
              type: number
            nro_pao:
              type: integer
            tiene_pedido:
              type: boolean
            es_regalo:
              type: boolean
            observaciones:
              type: string
            horario:
              type: string
    responses:
      200:
        description: Cliente actualizado con éxito
        schema:
          type: object
          properties:
            mensaje:
              type: string
      400:
        description: Datos de entrada inválidos
      404:
        description: Cliente no encontrado
      500:
        description: Error interno del servidor
    """
    datos_actualizados = request.get_json()
    if not datos_actualizados:
        return jsonify({"error": "No se proporcionaron datos para actualizar."}), 400

    with Session.begin() as session:
        try:
            resultado, mensaje = API.actualizarCliente(session, cliente_id, datos_actualizados)
            
            if resultado == "success":
                return jsonify({"mensaje": mensaje}), 200
            elif resultado == "not_found":
                return jsonify({"error": mensaje}), 404
            elif resultado == "error":
                return jsonify({"error": mensaje}), 400
            else:
                return jsonify({"error": "Error inesperado en la actualización."}), 500

        except Exception as e:
            app.logger.error(f"Error en /api/clientes/actualizar/{cliente_id}: {e}")
            return jsonify({"error": "Error interno del servidor al actualizar el cliente."}), 500

@app.route("/api/clientes/pedidos", methods=["GET"])
def get_clientes_con_pedidos():
    """
    Obtiene todos los clientes que tengan pedidos con coordenadas geográficas.
    ---
    tags:
      - Clientes
    responses:
      200:
        description: Lista de clientes con pedidos incluyendo coordenadas
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
              tiene_pedido:
                type: integer
              telefono:
                type: string
              cantidad:
                type: number
              horario:
                type: string
              nro_pao:
                type: integer
              observacion:
                type: string
              es_regalo:
                type: integer
              longitud:
                type: number
                description: Longitud en grados decimales (EPSG:4326)
              latitud:
                type: number
                description: Latitud en grados decimales (EPSG:4326)
      500:
        description: Error interno del servidor
    """
    with Session.begin() as session:
    # session = Session()
      try:         
          clientes = API.getClientesConPedidos(session)
          
          if clientes is None or len(clientes) == 0:
              return jsonify({"message": "No se encontraron clientes con pedidos"}), 200
          else:
              return jsonify(clientes), 200
      except Exception as e:
          app.logger.error(f"Error en /api/clientes/pedidos: {e}")
          return jsonify({"error": "Error interno del servidor al obtener clientes con pedidos."}), 500
      # finally:
      #     session.close()

if __name__ == '__main__':
    # Habilitar logging para ver errores de Flask y SQLAlchemy
    import logging
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler() # Log to stderr
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000, debug=True)
