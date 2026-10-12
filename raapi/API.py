# raapi/API.py
# coding=utf-8

from sqlalchemy import func, and_, or_, text
from decimal import Decimal
import datetime
import json
import re
from tables import Cliente, Pedido, Precio, Tramo

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

        registra_pedido = valores_actualizacion.get("tiene_pedido") == 1
        datos_pedido = None
        if registra_pedido:
            fecha_pedido = API._fecha_pedido(datos_actualizados)
            if fecha_pedido is None:
                return "error", "La fecha del pedido no es válida."

            precio_unitario = API._precio_unitario_vigente(session)
            if precio_unitario is None:
                return "error", "No hay un precio vigente para registrar el pedido."

            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).one()
            datos_pedido = {
                "fecha": datetime.datetime.combine(fecha_pedido, datetime.time.min),
                "id_cliente": cliente_id,
                "nombre": cliente.nombre,
                "turno": 1,
                "cantidad": valores_actualizacion.get("cantidad", cliente.cantidad),
                "direccion": cliente.direccion,
                "calle": cliente.calle,
                "altura": cliente.altura,
                "geometry": cliente.geometria,
                "observaciones": valores_actualizacion.get("observacion", cliente.observacion),
                "precio_unitario": precio_unitario,
                "nro_pao": valores_actualizacion.get("nro_pao", cliente.nro_pao),
            }

        # Ejecutar la actualización usando ORM
        try:
            result = session.query(Cliente).filter(Cliente.id == cliente_id).update(valores_actualizacion)
            if result > 0:
                if datos_pedido is not None:
                    session.add(Pedido(**datos_pedido))
                return "success", "Cliente actualizado correctamente."
            else:
                return "error", "No se pudo actualizar el cliente."
        except Exception as e:
            raise e  # Dejar que el contexto superior maneje la excepción

    @staticmethod
    def _fecha_pedido(datos_actualizados):
        """Usa la fecha recibida. Si no viene, el pedido queda para mañana."""
        if "fecha" not in datos_actualizados or datos_actualizados.get("fecha") in (None, ""):
            return datetime.date.today() + datetime.timedelta(days=1)

        value = datos_actualizados.get("fecha")
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, str):
            texto = value.strip()
            if not texto:
                return datetime.date.today() + datetime.timedelta(days=1)
            try:
                return datetime.date.fromisoformat(texto[:10])
            except ValueError:
                return None
        return None

    @staticmethod
    def _precio_unitario_vigente(session):
        """Precio del registro con la fecha más reciente."""
        fila = (
            session.query(Precio.precio)
            .order_by(Precio.fecha.desc(), Precio.id_precio.desc())
            .first()
        )
        if fila is None or fila[0] is None:
            return None
        return float(fila[0])

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
    def agregarCliente(session, datos_cliente):
        """
        Agrega un nuevo cliente a la base de datos.
        Retorna una tupla (resultado, mensaje/cliente_data) donde:
        - resultado: 'success', 'error', 'validation_error'
        - datos: diccionario con información del cliente creado o mensaje de error
        """
        try:
            # Validar campos requeridos
            if not datos_cliente.get('nombre'):
                return "validation_error", "El nombre del cliente es requerido."
            
            if not datos_cliente.get('direccion'):
                return "validation_error", "La dirección del cliente es requerida."
                
            if not datos_cliente.get('latitud') or not datos_cliente.get('longitud'):
                return "validation_error", "Las coordenadas (latitud y longitud) son requeridas."

            # Preparar datos para inserción
            nuevo_cliente = {
                'nombre': datos_cliente['nombre'].strip(),
                'direccion': datos_cliente['direccion'].strip(),
                'calle': datos_cliente.get('calle', '').strip() if datos_cliente.get('calle') else None,
                'altura': int(datos_cliente['altura']) if datos_cliente.get('altura') and str(datos_cliente['altura']).strip() else None,
                'tiene_pedido': 1 if datos_cliente.get('tiene_pedido') else 0,
                'telefono': datos_cliente.get('telefono', '').strip() if datos_cliente.get('telefono') else None,
                'cantidad': float(datos_cliente['cantidad']) if datos_cliente.get('cantidad') else 0.0,
                'horario': datos_cliente.get('horario') if datos_cliente.get('horario') else None,
                'nro_pao': int(datos_cliente['nro_pao']) if datos_cliente.get('nro_pao') and str(datos_cliente['nro_pao']).strip() else None,
                'observacion': datos_cliente.get('observacion', '').strip() if datos_cliente.get('observacion') else None,
                'es_regalo': 1 if datos_cliente.get('es_regalo') else 0
            }
            
            # Crear la geometría a partir de las coordenadas (convertir de EPSG:4326 a EPSG:5347)
            latitud = float(datos_cliente['latitud'])
            longitud = float(datos_cliente['longitud'])
            
            # Insertar el cliente usando SQL directo con la geometría
            insert_query = """
                INSERT INTO generalbelgrano.clientes 
                (nombre, direccion, calle, altura, tiene_pedido, telefono, cantidad, horario, nro_pao, observacion, es_regalo, geometria)
                VALUES 
                (:nombre, :direccion, :calle, :altura, :tiene_pedido, :telefono, :cantidad, :horario, :nro_pao, :observacion, :es_regalo, 
                 ST_Transform(ST_SetSRID(ST_MakePoint(:longitud, :latitud), 4326), 5347))
                RETURNING id, nombre, direccion, calle, altura, 
                         ST_X(ST_Transform(geometria, 4326)) as longitud,
                         ST_Y(ST_Transform(geometria, 4326)) as latitud
            """
            
            # Agregar coordenadas al diccionario de datos
            nuevo_cliente['latitud'] = latitud
            nuevo_cliente['longitud'] = longitud
            
            result = session.execute(text(insert_query), nuevo_cliente).fetchone()
            
            if result:
                cliente_creado = API.to_dict(result)
                return "success", cliente_creado
            else:
                return "error", "No se pudo crear el cliente."
                
        except ValueError as e:
            return "validation_error", f"Error en los datos proporcionados: {str(e)}"
        except Exception as e:
            raise e  # Dejar que el contexto superior maneje la excepción

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
    def getPedidosHistorico(session, desde=None, hasta=None):
        """
        Lista pedidos de la tabla pedido entre dos fechas, inclusive.
        Si no llegan fechas, usa el día del pedido más reciente.
        """
        ultima = session.query(func.max(Pedido.fecha)).scalar()
        if ultima is None:
            return {"fecha_desde": None, "fecha_hasta": None, "pedidos": []}

        dia_ultimo = ultima.date() if isinstance(ultima, datetime.datetime) else ultima
        if desde is None and hasta is None:
            desde = dia_ultimo
            hasta = dia_ultimo
        elif desde is None or hasta is None:
            raise ValueError("Indicá la fecha desde y la fecha hasta.")
        if desde > hasta:
            raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")

        inicio = datetime.datetime.combine(desde, datetime.time.min)
        fin = datetime.datetime.combine(hasta + datetime.timedelta(days=1), datetime.time.min)
        result = (
            session.query(
                Pedido.id_pedido.label("id"),
                Pedido.id_cliente,
                Pedido.nombre,
                Pedido.direccion,
                Pedido.cantidad,
                Cliente.telefono,
                Cliente.horario,
                Pedido.nro_pao,
                Cliente.es_regalo,
                Pedido.precio_unitario,
                Pedido.observaciones.label("observacion"),
                func.ST_X(func.ST_Transform(Pedido.geometry, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Pedido.geometry, 4326)).label("latitud")
            )
            .outerjoin(Cliente, Cliente.id == Pedido.id_cliente)
            .filter(Pedido.fecha >= inicio, Pedido.fecha < fin)
            .order_by(Pedido.id_pedido)
            .all()
        )
        return {
            "fecha_desde": desde.isoformat(),
            "fecha_hasta": hasta.isoformat(),
            "pedidos": [API.to_dict(row) for row in result]
        }

    @staticmethod
    def eliminarPedido(session, id_pedido):
        """
        Elimina el pedido y deja al cliente sin pedido activo.
        """
        pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).one_or_none()
        if pedido is None:
            return "not_found", "Pedido no encontrado."

        id_cliente = pedido.id_cliente
        session.delete(pedido)
        if id_cliente is not None:
            session.query(Cliente).filter(Cliente.id == id_cliente).update(
                {
                    "tiene_pedido": 0,
                    "cantidad": 1,
                    "horario": None,
                    "nro_pao": None,
                    "es_regalo": 0,
                },
                synchronize_session=False,
            )
        session.flush()
        return "success", "Pedido eliminado correctamente."

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
            # El callejero guarda "Av Italia"; quien busca suele escribir "Italia 50".
            # Primero el nombre exacto. Si no hay tramo, el nombre al final del de la calle.
            nombre = func.upper(nombre_calle)
            calle = func.upper(Tramo.calle)
            misma_vereda = func.mod(Tramo.desde, 2) == (altura % 2)
            consulta = session.query(
                Tramo.id,
                Tramo.calle,
                Tramo.desde,
                Tramo.hasta,
                func.ST_AsGeoJSON(func.ST_Transform(func.ST_Centroid(Tramo.geometry), 4326)).label("centroide_geojson")
            ).filter(
                Tramo.desde <= altura,
                altura <= Tramo.hasta
            ).order_by(misma_vereda.desc(), func.length(Tramo.calle))

            result = consulta.filter(calle == nombre).first()
            if result is None:
                result = consulta.filter(calle.like("% " + nombre_calle)).first()

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