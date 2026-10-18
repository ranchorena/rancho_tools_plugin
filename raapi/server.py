# server.py
# coding=utf-8

from flask import Flask, request, jsonify
from markupsafe import escape
import json, os, requests

from config import Session
from datetime import datetime
from flask_cors import CORS
from flasgger import Swagger
from sqlalchemy import text # Para ejecutar SQL directamente si es necesario
# --- Nuevos Endpoints para Clientes ---
from API import API # Importar la clase/módulo con la lógica de BD
from auth import identidad_actual, instalar_autenticacion

app = Flask(__name__)
_origenes = [origen.strip() for origen in os.environ.get("CORS_ORIGINS", "http://localhost:8080").split(",") if origen.strip()]
CORS(
    app,
    origins=_origenes,
    allow_headers=["Authorization", "Content-Type", "Accept"],
    methods=["GET", "POST", "PUT", "OPTIONS"],
)
instalar_autenticacion(app)

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

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/direcciones/buscar", methods=["POST"])
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
            app.logger.error(f"Error en /api/direcciones/buscar: {e}")
            return jsonify({"error": "Error interno del servidor al procesar la búsqueda."}), 500


@app.route("/api/clientes/buscar", methods=["POST"])
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
            fecha:
              type: string
              format: date
              description: Fecha del pedido. Si tiene_pedido es verdadero y no se envía, se usa el día siguiente. Si el cliente ya tiene un pedido ese día, se actualiza.
            direccion:
              type: string
              description: Dirección del cliente. No crea un pedido.
            calle:
              type: string
            altura:
              type: integer
            telefono:
              type: string
            direccion_pedido:
              type: string
              description: Dirección que se guarda en el pedido. No modifica la dirección del cliente.
            latitud:
              type: number
              description: Latitud del pedido. Si no se envía, el pedido usa la geometría del cliente.
            longitud:
              type: number
              description: Longitud del pedido. Si no se envía, el pedido usa la geometría del cliente.
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
                identidad = identidad_actual() or {}
                if datos_actualizados.get("tiene_pedido"):
                    app.logger.info(
                        "pedido registrado cliente_id=%s sub=%s preferred_username=%s email=%s",
                        cliente_id,
                        identidad.get("sub"),
                        identidad.get("preferred_username"),
                        identidad.get("email"),
                    )
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

@app.route("/api/clientes/agregar", methods=["POST"])
def agregar_cliente_api():
    """
    Agrega un nuevo cliente a la base de datos.
    ---
    tags:
      - Clientes
    summary: Agregar nuevo cliente
    description: |
      Crea un nuevo cliente en la base de datos con los datos proporcionados.
      Las coordenadas deben estar en formato EPSG:4326 (WGS84) y serán convertidas automáticamente al sistema de coordenadas local.
      
      **Campos requeridos:**
      - nombre: Nombre del cliente
      - direccion: Dirección completa del cliente
      - latitud: Latitud en grados decimales (EPSG:4326)
      - longitud: Longitud en grados decimales (EPSG:4326)
    parameters:
      - name: body
        in: body
        required: true
        description: Datos del nuevo cliente
        schema:
          type: object
          required:
            - nombre
            - direccion
            - latitud
            - longitud
          properties:
            nombre:
              type: string
              description: "Nombre completo del cliente"
              example: "Juan Pérez"
              maxLength: 60
            direccion:
              type: string
              description: "Dirección completa del cliente"
              example: "San Martín 1250"
              maxLength: 50
            calle:
              type: string
              description: "Nombre de la calle (opcional, se puede extraer de dirección)"
              example: "San Martín"
              maxLength: 50
            altura:
              type: integer
              description: "Altura de la calle (opcional)"
              example: 1250
            telefono:
              type: string
              description: "Número de teléfono del cliente"
              example: "+54 11 1234-5678"
              maxLength: 30
            tiene_pedido:
              type: boolean
              description: "Si el cliente tiene pedido activo"
              example: false
            cantidad:
              type: number
              format: float
              description: "Cantidad de productos pedidos"
              example: 2.5
            horario:
              type: string
              format: time
              description: "Horario preferido de entrega (HH:MM)"
              example: "14:30"
            fecha:
              type: string
              format: date
              description: "Fecha del pedido (YYYY-MM-DD). Vacía por defecto. Si tiene_pedido es verdadero y no se envía, se usa el día siguiente."
              example: "2026-10-19"
            nro_pao:
              type: integer
              description: "Número de PAO"
              example: 123
            observacion:
              type: string
              description: "Observaciones adicionales"
              example: "Casa con portón azul"
              maxLength: 200
            es_regalo:
              type: boolean
              description: "Si el pedido es un regalo"
              example: false
            latitud:
              type: number
              format: float
              description: "Latitud en grados decimales (EPSG:4326/WGS84)"
              example: -34.6118
            longitud:
              type: number
              format: float
              description: "Longitud en grados decimales (EPSG:4326/WGS84)"
              example: -58.4173
          examples:
            cliente_basico:
              summary: "Cliente básico"
              value:
                nombre: "Juan Pérez"
                direccion: "San Martín 1250"
                latitud: -34.6118
                longitud: -58.4173
            cliente_completo:
              summary: "Cliente con todos los datos"
              value:
                nombre: "María González"
                direccion: "Av. Rivadavia 2540"
                calle: "Av. Rivadavia"
                altura: 2540
                telefono: "+54 11 1234-5678"
                tiene_pedido: true
                cantidad: 3.0
                fecha: "2026-10-19"
                horario: "15:00"
                nro_pao: 456
                observacion: "Timbre roto, golpear puerta"
                es_regalo: false
                latitud: -34.6037
                longitud: -58.3816
    responses:
      201:
        description: Cliente creado exitosamente
        schema:
          type: object
          properties:
            mensaje:
              type: string
              description: "Mensaje de éxito"
            cliente:
              type: object
              properties:
                id:
                  type: integer
                  description: "ID único del cliente creado"
                nombre:
                  type: string
                direccion:
                  type: string
                calle:
                  type: string
                altura:
                  type: integer
                longitud:
                  type: number
                  format: float
                latitud:
                  type: number
                  format: float
        examples:
          cliente_creado:
            summary: "Cliente creado exitosamente"
            value:
              mensaje: "Cliente agregado correctamente."
              cliente:
                id: 789
                nombre: "Juan Pérez"
                direccion: "San Martín 1250"
                calle: "San Martín"
                altura: 1250
                longitud: -58.4173
                latitud: -34.6118
      400:
        description: Datos de entrada inválidos
        schema:
          type: object
          properties:
            error:
              type: string
              description: "Descripción del error de validación"
        examples:
          datos_faltantes:
            summary: "Datos requeridos faltantes"
            value:
              error: "El nombre del cliente es requerido."
          coordenadas_invalidas:
            summary: "Coordenadas inválidas"
            value:
              error: "Las coordenadas (latitud y longitud) son requeridas."
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
              error: "Error interno del servidor al agregar el cliente."
    """
    datos_cliente = request.get_json()
    if not datos_cliente:
        return jsonify({"error": "No se proporcionaron datos del cliente."}), 400

    with Session.begin() as session:
        try:
            resultado, datos = API.agregarCliente(session, datos_cliente)
            
            if resultado == "success":
                return jsonify({
                    "mensaje": "Cliente agregado correctamente.",
                    "cliente": datos
                }), 201
            elif resultado == "validation_error":
                return jsonify({"error": datos}), 400
            elif resultado == "error":
                return jsonify({"error": datos}), 400
            else:
                return jsonify({"error": "Error inesperado al agregar el cliente."}), 500

        except Exception as e:
            app.logger.error(f"Error en /api/clientes/agregar: {e}")
            return jsonify({"error": "Error interno del servidor al agregar el cliente."}), 500

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

@app.route("/api/clientes/<int:cliente_id>/pedido", methods=["GET"])
def get_pedido_de_fecha(cliente_id):
    """
    Devuelve el pedido del cliente para una fecha.
    ---
    tags:
      - Pedidos
    parameters:
      - name: cliente_id
        in: path
        type: integer
        required: true
      - name: fecha
        in: query
        type: string
        format: date
        required: true
    responses:
      200:
        description: Pedido de esa fecha, o pedido null si no hay
      400:
        description: Fecha inválida
      404:
        description: Cliente no encontrado
    """
    valor = request.args.get("fecha")
    if valor is None or valor.strip() == "":
        return jsonify({"error": "La fecha del pedido es requerida."}), 400
    try:
        fecha = datetime.strptime(valor.strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "La fecha del pedido no es válida."}), 400

    with Session.begin() as session:
        try:
            resultado, pedido = API.getPedidoDeFecha(session, cliente_id, fecha)
            if resultado == "not_found":
                return jsonify({"error": f"Cliente con ID {cliente_id} no encontrado."}), 404
            return jsonify({"pedido": pedido}), 200
        except Exception as e:
            app.logger.error(f"Error en /api/clientes/{cliente_id}/pedido: {e}")
            return jsonify({"error": "Error interno del servidor al obtener el pedido."}), 500

@app.route("/api/pedidos/cercano", methods=["GET"])
def get_pedido_cercano():
    """
    Devuelve el pedido activo más cercano a una latitud y longitud.
    ---
    tags:
      - Pedidos
    parameters:
      - name: latitud
        in: query
        type: number
        required: true
      - name: longitud
        in: query
        type: number
        required: true
    responses:
      200:
        description: Pedido más cercano, o pedido null si no hay pedidos activos
      400:
        description: Coordenadas inválidas
    """
    def parse_coord(nombre, minimo, maximo):
        valor = request.args.get(nombre)
        if valor is None or valor.strip() == "":
            return None, f"La {nombre} es requerida."
        try:
            numero = float(valor)
        except ValueError:
            return None, f"La {nombre} no es válida."
        if numero < minimo or numero > maximo:
            return None, f"La {nombre} no es válida."
        return numero, None

    latitud, error_lat = parse_coord("latitud", -90, 90)
    if error_lat:
        return jsonify({"error": error_lat}), 400
    longitud, error_lon = parse_coord("longitud", -180, 180)
    if error_lon:
        return jsonify({"error": error_lon}), 400

    with Session.begin() as session:
        try:
            pedido = API.getPedidoCercano(session, latitud, longitud)
            return jsonify({"pedido": pedido}), 200
        except Exception as e:
            app.logger.error(f"Error en /api/pedidos/cercano: {e}")
            return jsonify({"error": "Error interno del servidor al buscar el pedido más cercano."}), 500

@app.route("/api/pedidos/historico", methods=["GET"])
def get_pedidos_historico():
    """
    Obtiene pedidos de la tabla pedido entre fecha desde y fecha hasta.
    Sin fechas, usa el día del último pedido.
    ---
    tags:
      - Pedidos
    parameters:
      - name: desde
        in: query
        type: string
        format: date
        required: false
      - name: hasta
        in: query
        type: string
        format: date
        required: false
    responses:
      200:
        description: Pedidos del rango y las fechas aplicadas
      400:
        description: Fechas inválidas
      500:
        description: Error interno del servidor
    """
    def parse_fecha(nombre):
        valor = request.args.get(nombre)
        if valor is None or valor.strip() == "":
            return None
        try:
            return datetime.strptime(valor.strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"La fecha {nombre} no es válida.")

    try:
        desde = parse_fecha("desde")
        hasta = parse_fecha("hasta")
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    with Session.begin() as session:
        try:
            datos = API.getPedidosHistorico(session, desde, hasta)
            return jsonify(datos), 200
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except Exception as e:
            app.logger.error(f"Error en /api/pedidos/historico: {e}")
            return jsonify({"error": "Error interno del servidor al obtener el historial de pedidos."}), 500

@app.route("/api/pedidos/eliminar", methods=["POST"])
def eliminar_pedido_api():
    """
    Elimina un pedido. Si el cliente conserva otro pedido de hoy o posterior, tiene_pedido sigue en 1.
    ---
    tags:
      - Pedidos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_pedido
          properties:
            id_pedido:
              type: integer
    responses:
      200:
        description: Pedido eliminado
      400:
        description: Datos inválidos
      404:
        description: Pedido no encontrado
      500:
        description: Error interno del servidor
    """
    datos = request.get_json(silent=True) or {}
    id_pedido = datos.get("id_pedido")
    if not isinstance(id_pedido, int) or isinstance(id_pedido, bool) or id_pedido <= 0:
        return jsonify({"error": "Indicá el id_pedido a eliminar."}), 400

    with Session.begin() as session:
        try:
            resultado, mensaje = API.eliminarPedido(session, id_pedido)
            if resultado == "success":
                return jsonify({"mensaje": mensaje}), 200
            if resultado == "not_found":
                return jsonify({"error": mensaje}), 404
            return jsonify({"error": mensaje}), 400
        except Exception as e:
            app.logger.error(f"Error en /api/pedidos/eliminar: {e}")
            return jsonify({"error": "Error interno del servidor al eliminar el pedido."}), 500

@app.route("/api/pedidos/iniciar", methods=["POST"])
def iniciar_pedidos_api():
    """
    Deja sin pedido activo a los clientes que tienen tiene_pedido=1.
    ---
    tags:
      - Pedidos
    responses:
      200:
        description: Clientes actualizados
      500:
        description: Error interno del servidor
    """
    with Session.begin() as session:
        try:
            resultado, mensaje = API.iniciarPedidos(session)
            if resultado == "success":
                return jsonify({"mensaje": mensaje}), 200
            return jsonify({"error": mensaje}), 400
        except Exception as e:
            app.logger.error(f"Error en /api/pedidos/iniciar: {e}")
            return jsonify({"error": "Error interno del servidor al iniciar los pedidos."}), 500

if __name__ == '__main__':
    # Habilitar logging para ver errores de Flask y SQLAlchemy
    import logging
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler() # Log to stderr
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000, debug=True)
