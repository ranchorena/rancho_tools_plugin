# raapi/API.py
# coding=utf-8

from sqlalchemy import func, and_, or_
from decimal import Decimal
import datetime
import json
import re
from tables import Cliente, Tramo

class API: # Clase contenedora renombrada a API
    @staticmethod
    def to_dict(row):
        """Convierte una fila de SQLAlchemy (o similar con ._mapping) a un diccionario, 
        manejando tipos de datos especiales como time, datetime, Decimal."""
        if row is None:
            return None
        
        if hasattr(row, '_mapping'):
            data = dict(row._mapping)
        else:
            data = {key: value for key, value in row.items()}
        
        # Convertir tipos especiales a formatos serializables JSON
        for key, value in data.items():
            if isinstance(value, datetime.time):
                data[key] = value.strftime('%H:%M:%S') if value else None
            elif isinstance(value, datetime.datetime):
                data[key] = value.isoformat() if value else None
            elif isinstance(value, datetime.date):
                data[key] = value.isoformat() if value else None
            elif isinstance(value, Decimal):
                data[key] = float(value) if value is not None else None
        
        return data

    @staticmethod
    def buscar_cliente_por_nombre(session, nombre_cliente):
        """
        Busca clientes donde el campo nombre contenga nombre_cliente (insensible a mayúsculas/minúsculas).
        Retorna una lista de diccionarios de cliente con Id, Nombre, Direccion, Calle, Altura y coordenadas.
        """
        result = (
            session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.direccion,
                Cliente.calle,
                Cliente.altura,
                func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud")
            )
            .filter(
                and_(
                    func.lower(Cliente.nombre).like(func.lower(f"%{nombre_cliente}%")),
                    Cliente.geometria.isnot(None)
                )
            )
            .all()
        )
        
        clientes = [API.to_dict(row) for row in result]
        return clientes

    @staticmethod
    def buscar_clientes_por_direccion(session, direccion_buscada):
        """
        Busca clientes donde el campo direccion contenga direccion_buscada (insensible a mayúsculas/minúsculas).
        Retorna una lista de diccionarios de cliente con Id, Nombre, Direccion, Calle, Altura y coordenadas.
        """
        result = (
            session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.direccion,
                Cliente.calle,
                Cliente.altura,
                func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud")
            )
            .filter(
                and_(
                    func.lower(Cliente.direccion).like(func.lower(f"%{direccion_buscada}%")),
                    Cliente.geometria.isnot(None)
                )
            )
            .all()
        )
        
        clientes = [API.to_dict(row) for row in result]
        return clientes

    @staticmethod
    def buscar_clientes_por_calle_altura(session, calle_buscada, altura_buscada=None):
        """
        Busca clientes donde el campo calle O direccion contenga calle_buscada (insensible a mayúsculas/minúsculas).
        Si altura_buscada se proporciona, también filtra por altura.
        Retorna una lista de diccionarios de cliente con Id, Nombre, Direccion, Calle, Altura y coordenadas.
        """
        # Construir filtros base - buscar tanto en calle como en direccion
        filtros = [
            # Buscar en campo calle O en campo direccion
            or_(
                func.lower(Cliente.calle).like(func.lower(f"%{calle_buscada}%")),
                func.lower(Cliente.direccion).like(func.lower(f"%{calle_buscada}%"))
            ),
            Cliente.geometria.isnot(None)
        ]

        # Agregar filtro de altura si se proporciona
        if altura_buscada is not None and altura_buscada != "":
            try:
                altura_int = int(altura_buscada)
                filtros.append(Cliente.altura == altura_int)
            except ValueError:
                pass  # Si no se puede convertir a int, ignorar filtro de altura

        result = (
            session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.direccion,
                Cliente.calle,
                Cliente.altura,
                func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud")
            )
            .filter(and_(*filtros))
            .all()
        )
        
        clientes = [API.to_dict(row) for row in result]
        return clientes



    @staticmethod
    def actualizarCliente(session, cliente_id, datos_actualizados):
        """
        Actualiza un cliente existente con nueva estructura simplificada.
        Retorna el resultado de la operación: 'success', 'not_found', o 'error'
        """
        # Mapeo de campos del DTO a campos de la base de datos
        mapa_campos = {
            "docenas": "cantidad",
            "nro_pao": "nro_pao", 
            "tiene_pedido": "tiene_pedido",
            "es_regalo": "es_regalo",
            "observaciones": "observacion",
            "horario": "horario"
        }

        # Filtrar solo los campos permitidos
        allowed_fields = set(mapa_campos.keys())
        datos_filtrados = {k: v for k, v in datos_actualizados.items() if k in allowed_fields}
        
        if not datos_filtrados:
            return "error", "No se proporcionaron campos válidos para actualizar."

        # Verificar si el cliente existe
        existe = session.query(Cliente.id).filter(Cliente.id == cliente_id).first()
        if not existe:
            return "not_found", f"Cliente con ID {cliente_id} no encontrado."

        # Construir diccionario de valores para actualizar
        valores_actualizacion = {}

        for key_dto, value_dto in datos_filtrados.items():
            db_column_name = mapa_campos[key_dto]
            
            # Procesar tipos de datos específicos
            if key_dto in ["tiene_pedido", "es_regalo"]:
                valores_actualizacion[db_column_name] = 1 if value_dto else 0
            elif key_dto == "horario":
                valores_actualizacion[db_column_name] = value_dto if value_dto else None
            elif key_dto == "docenas":
                valores_actualizacion[db_column_name] = float(value_dto) if value_dto is not None else None
            elif key_dto == "nro_pao":
                valores_actualizacion[db_column_name] = int(value_dto) if value_dto is not None else None
            else:
                valores_actualizacion[db_column_name] = value_dto

        # Ejecutar la actualización usando ORM
        try:
            result = session.query(Cliente).filter(Cliente.id == cliente_id).update(valores_actualizacion)
            if result > 0:
                return "success", "Cliente actualizado correctamente."
            else:
                return "error", "No se pudo actualizar el cliente."
        except Exception as e:
            raise e  # Dejar que el contexto superior maneje la excepción

    @staticmethod
    def getClienteById(session, id_cliente):
        """
        Obtiene un cliente específico por su ID.
        Retorna un diccionario con los datos del cliente incluyendo coordenadas o None si no se encuentra.
        """
        result = (
            session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.direccion,
                Cliente.calle,
                Cliente.altura,
                Cliente.tiene_pedido,
                Cliente.telefono,
                Cliente.cantidad,
                Cliente.horario,
                Cliente.nro_pao,
                Cliente.observacion,
                Cliente.es_regalo,
                func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud")
            )
            .filter(Cliente.id == id_cliente)
            .first()
        )
        
        return API.to_dict(result) if result else None

    @staticmethod
    def getClientesConPedidos(session):
        """
        Obtiene todos los clientes que tengan pedidos (tiene_pedido=1).
        Retorna una lista de diccionarios con los datos de los clientes incluyendo coordenadas.
        """
        result = (
            session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.direccion,
                Cliente.calle,
                Cliente.altura,
                Cliente.tiene_pedido,
                Cliente.telefono,
                Cliente.cantidad,
                Cliente.horario,
                Cliente.nro_pao,
                Cliente.observacion,
                Cliente.es_regalo,
                func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud")
            )
            .filter(
                and_(
                    Cliente.tiene_pedido == 1,
                    Cliente.geometria.isnot(None)
                )
            )
            .all()
        )
        
        clientes = [API.to_dict(row) for row in result]
        return clientes

    @staticmethod
    def parse_direccion(direccion_str):
        """
        Parsea una dirección completa en calle y altura.
        Retorna (calle, altura) o (None, None) si no se puede parsear.
        """
        # Intenta encontrar un número al final de la cadena, precedido opcionalmente por espacios.
        # El resto será considerado el nombre de la calle.
        match = re.match(r"^(.*?)\s*(\d+)\s*$", direccion_str.strip())
        if match:
            calle = match.group(1).strip().upper()  # Convertir a mayúsculas para comparar
            try:
                altura = int(match.group(2))
                return calle, altura
            except ValueError:
                return None, None  # No es un número válido
        # Si no hay número, podría ser solo el nombre de la calle (sin altura)
        # o un formato no esperado. Por ahora, si no hay número, no lo manejamos específicamente.
        # Podríamos buscar la calle sin altura, pero la lógica se complica.
        # Para este caso, si no hay altura, devolvemos la dirección completa como calle.
        # Esto requeriría que la búsqueda SQL maneje el caso de altura NULL o no filtrar por altura.
        # Por ahora, requerimos una altura.
        return None, None

    @staticmethod
    def buscarDireccion(session, direccion_completa):
        """
        Busca una dirección (calle y altura) y devuelve el punto medio del tramo correspondiente.
        Retorna una tupla (resultado, datos) donde:
        - resultado: 'success', 'not_found', 'invalid_format', 'geometry_error'
        - datos: diccionario con latitud, longitud y tramo_info o mensaje de error
        """
        # Parsear la dirección
        nombre_calle, altura = API.parse_direccion(direccion_completa)
        
        if not nombre_calle or altura is None:
            return "invalid_format", {
                "error": "Formato de dirección incorrecto. Se espera 'Nombre de Calle Número' (ej. SARMIENTO 550)."
            }

        try:
            # Usar SQLAlchemy ORM para buscar el tramo
            # Usamos ST_Centroid para obtener el punto medio y ST_Transform para convertir a EPSG:4326 (lat/lon)
            # La función ST_AsGeoJSON se usa para extraer las coordenadas del punto.
            # El SRID original es 5347 según el DDL.
            # La búsqueda de calle es case-insensitive usando func.upper() en ambos lados.
            result = (
                session.query(
                    Tramo.id,
                    Tramo.calle,
                    Tramo.desde,
                    Tramo.hasta,
                    func.ST_AsGeoJSON(func.ST_Transform(func.ST_Centroid(Tramo.geometry), 4326)).label("centroide_geojson")
                )
                .filter(
                    and_(
                        func.upper(Tramo.calle) == func.upper(nombre_calle),
                        Tramo.desde <= altura,
                        altura <= Tramo.hasta
                    )
                )
                .first()
            )

            if result:
                tramo_id, tramo_calle, tramo_desde, tramo_hasta, centroide_geojson_str = result

                if centroide_geojson_str:
                    centroide_geojson = json.loads(centroide_geojson_str)
                    # GeoJSON para un Point tiene las coordenadas en formato [longitud, latitud]
                    longitud, latitud = centroide_geojson['coordinates']

                    return "success", {
                        "latitud": latitud,
                        "longitud": longitud,
                        "tramo_info": {
                            "id": tramo_id,
                            "nombre_calle": tramo_calle,
                            "desde": tramo_desde,
                            "hasta": tramo_hasta
                        }
                    }
                else:
                    # Esto no debería pasar si la geometría existe y ST_Centroid funciona.
                    return "geometry_error", {
                        "error": "No se pudo calcular el centroide para el tramo encontrado."
                    }
            else:
                # Podríamos dar un mensaje más específico si la calle existe pero la altura no.
                # Para ello, haríamos una primera consulta por la calle y luego verificaríamos la altura.
                # Por ahora, un 404 general es suficiente.
                return "not_found", {
                    "error": f"Dirección no encontrada: Calle '{nombre_calle}' con altura {altura} no existe o altura fuera de rango."
                }

        except Exception as e:
            # Re-lanzar la excepción para que sea manejada por el contexto superior
            raise e