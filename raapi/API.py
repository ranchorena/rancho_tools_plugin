# raapi/API.py
# coding=utf-8

from sqlalchemy import func, and_, or_, text
from decimal import Decimal
import datetime
import json
import re
from tables import Cliente, Pedido, Precio, Tramo
from config import schema

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
                Cliente.telefono,
                Cliente.tiene_pedido,
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
                Cliente.telefono,
                Cliente.tiene_pedido,
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
                Cliente.telefono,
                Cliente.tiene_pedido,
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
            "horario": "horario",
            "direccion": "direccion",
            "calle": "calle",
            "altura": "altura",
            "telefono": "telefono",
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
            elif key_dto == "direccion":
                texto = str(value_dto).strip() if value_dto is not None else ""
                if not texto:
                    return "error", "La dirección del cliente es requerida."
                valores_actualizacion[db_column_name] = texto
            elif key_dto == "altura":
                if value_dto in (None, ""):
                    valores_actualizacion[db_column_name] = None
                else:
                    try:
                        valores_actualizacion[db_column_name] = int(value_dto)
                    except (TypeError, ValueError):
                        return "error", "La altura no es válida."
            elif key_dto in ("calle", "telefono"):
                texto = str(value_dto).strip() if value_dto is not None else ""
                valores_actualizacion[db_column_name] = texto or None
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
            direccion_pedido = datos_actualizados.get("direccion_pedido")
            if isinstance(direccion_pedido, str):
                direccion_pedido = direccion_pedido.strip() or None
            else:
                direccion_pedido = None
            calle_pedido, altura_pedido = (None, None)
            if direccion_pedido:
                calle_pedido, altura_pedido = API.parse_direccion(direccion_pedido)
            punto = API._punto_pedido(datos_actualizados)
            if punto is False:
                return "error", "La ubicación del pedido no es válida."
            datos_pedido = {
                "fecha": datetime.datetime.combine(fecha_pedido, datetime.time.min),
                "id_cliente": cliente_id,
                "nombre": cliente.nombre,
                "turno": 1,
                "cantidad": valores_actualizacion["cantidad"] if "cantidad" in valores_actualizacion and valores_actualizacion["cantidad"] is not None else cliente.cantidad,
                "direccion": direccion_pedido or cliente.direccion,
                "calle": calle_pedido or cliente.calle,
                "altura": altura_pedido if altura_pedido is not None else cliente.altura,
                "observaciones": valores_actualizacion.get("observacion", cliente.observacion),
                "precio_unitario": precio_unitario,
                "nro_pao": valores_actualizacion.get("nro_pao", cliente.nro_pao),
            }
            if punto is None:
                datos_pedido["geometry"] = cliente.geometria
            else:
                datos_pedido["lon"] = float(datos_actualizados["longitud"])
                datos_pedido["lat"] = float(datos_actualizados["latitud"])

        # Ejecutar la actualización usando ORM
        try:
            result = session.query(Cliente).filter(Cliente.id == cliente_id).update(valores_actualizacion)
            if result > 0:
                if datos_pedido is not None:
                    mensaje = API._guardar_pedido(session, datos_pedido)
                    return "success", mensaje
                return "success", "Cliente actualizado correctamente."
            else:
                return "error", "No se pudo actualizar el cliente."
        except Exception as e:
            raise e  # Dejar que el contexto superior maneje la excepción

    @staticmethod
    def _guardar_pedido(session, datos_pedido):
        """Actualiza el pedido del cliente para esa fecha. Si no existe, lo inserta."""
        inicio = datos_pedido["fecha"]
        fin = inicio + datetime.timedelta(days=1)
        existente = (
            session.query(Pedido.id_pedido)
            .filter(
                Pedido.id_cliente == datos_pedido["id_cliente"],
                Pedido.fecha >= inicio,
                Pedido.fecha < fin,
            )
            .order_by(Pedido.id_pedido.desc())
            .first()
        )
        if existente is None:
            if "lon" in datos_pedido:
                session.execute(text(f"""
                    INSERT INTO {schema}.pedido
                    (fecha, id_cliente, nombre, turno, cantidad, direccion, calle, altura, geometry, observaciones, precio_unitario, nro_pao)
                    VALUES
                    (:fecha, :id_cliente, :nombre, :turno, :cantidad, :direccion, :calle, :altura,
                     ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 5347),
                     :observaciones, :precio_unitario, :nro_pao)
                """), datos_pedido)
            else:
                session.add(Pedido(**datos_pedido))
            return "Pedido registrado correctamente."

        parametros = {
            "id_pedido": existente[0],
            "fecha": datos_pedido["fecha"],
            "id_cliente": datos_pedido["id_cliente"],
            "nombre": datos_pedido["nombre"],
            "turno": datos_pedido["turno"],
            "cantidad": datos_pedido["cantidad"],
            "direccion": datos_pedido["direccion"],
            "calle": datos_pedido["calle"],
            "altura": datos_pedido["altura"],
            "observaciones": datos_pedido["observaciones"],
            "nro_pao": datos_pedido["nro_pao"],
        }
        if "lon" in datos_pedido:
            parametros["lon"] = datos_pedido["lon"]
            parametros["lat"] = datos_pedido["lat"]
            geometry_sql = "ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 5347)"
        else:
            geometry_sql = f"(SELECT geometria FROM {schema}.clientes WHERE id = :id_cliente)"
        session.execute(text(f"""
            UPDATE {schema}.pedido SET
                fecha = :fecha,
                nombre = :nombre,
                turno = :turno,
                cantidad = :cantidad,
                direccion = :direccion,
                calle = :calle,
                altura = :altura,
                observaciones = :observaciones,
                nro_pao = :nro_pao,
                geometry = {geometry_sql}
            WHERE id_pedido = :id_pedido
        """), parametros)
        return "Pedido actualizado correctamente."

    @staticmethod
    def getPedidoDeFecha(session, cliente_id, fecha):
        """Devuelve el pedido más reciente del cliente para ese día, o None."""
        existe = session.query(Cliente.id).filter(Cliente.id == cliente_id).first()
        if existe is None:
            return "not_found", None

        inicio = datetime.datetime.combine(fecha, datetime.time.min)
        fin = inicio + datetime.timedelta(days=1)
        row = (
            session.query(
                Pedido.id_pedido.label("id"),
                Pedido.fecha,
                Pedido.cantidad,
                Pedido.direccion,
                Pedido.calle,
                Pedido.altura,
                Pedido.nro_pao,
                Pedido.observaciones.label("observacion"),
                func.ST_X(func.ST_Transform(Pedido.geometry, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Pedido.geometry, 4326)).label("latitud"),
            )
            .filter(
                Pedido.id_cliente == cliente_id,
                Pedido.fecha >= inicio,
                Pedido.fecha < fin,
            )
            .order_by(Pedido.id_pedido.desc())
            .first()
        )
        if row is None:
            return "empty", None
        pedido = API.to_dict(row)
        if isinstance(pedido.get("fecha"), str):
            pedido["fecha"] = pedido["fecha"][:10]
        return "success", pedido

    @staticmethod
    def _punto_pedido(datos_actualizados):
        """Geometría del pedido en EPSG:5347. None conserva la del cliente. False si no es válida."""
        if "latitud" not in datos_actualizados and "longitud" not in datos_actualizados:
            return None
        latitud = datos_actualizados.get("latitud")
        longitud = datos_actualizados.get("longitud")
        if latitud in (None, "") and longitud in (None, ""):
            return None
        try:
            latitud = float(latitud)
            longitud = float(longitud)
        except (TypeError, ValueError):
            return False
        return func.ST_Transform(func.ST_SetSRID(func.ST_MakePoint(longitud, latitud), 4326), 5347)

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

            registra_pedido = 1 if datos_cliente.get('tiene_pedido') else 0
            fecha_pedido = None
            precio_unitario = None
            if registra_pedido:
                fecha_pedido = API._fecha_pedido(datos_cliente)
                if fecha_pedido is None:
                    return "validation_error", "La fecha del pedido no es válida."
                precio_unitario = API._precio_unitario_vigente(session)
                if precio_unitario is None:
                    return "error", "No hay un precio vigente para registrar el pedido."

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
                if registra_pedido:
                    cliente = session.query(Cliente).filter(Cliente.id == cliente_creado["id"]).one()
                    session.add(Pedido(
                        fecha=datetime.datetime.combine(fecha_pedido, datetime.time.min),
                        id_cliente=cliente.id,
                        nombre=cliente.nombre,
                        turno=1,
                        cantidad=nuevo_cliente["cantidad"],
                        direccion=cliente.direccion,
                        calle=cliente.calle,
                        altura=cliente.altura,
                        geometry=cliente.geometria,
                        observaciones=nuevo_cliente["observacion"],
                        precio_unitario=precio_unitario,
                        nro_pao=nuevo_cliente["nro_pao"],
                    ))
                    session.flush()
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
    def getPedidoCercano(session, latitud, longitud):
        """
        Devuelve el cliente con pedido activo más cercano al punto, en metros.
        El punto llega en EPSG:4326 y se compara en EPSG:5347.
        """
        punto = func.ST_Transform(func.ST_SetSRID(func.ST_MakePoint(longitud, latitud), 4326), 5347)
        distancia = func.ST_Distance(Cliente.geometria, punto).label("distancia")
        row = (
            session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.direccion,
                Cliente.calle,
                Cliente.altura,
                Cliente.telefono,
                Cliente.cantidad,
                Cliente.horario,
                Cliente.observacion,
                func.ST_X(func.ST_Transform(Cliente.geometria, 4326)).label("longitud"),
                func.ST_Y(func.ST_Transform(Cliente.geometria, 4326)).label("latitud"),
                distancia,
            )
            .filter(and_(Cliente.tiene_pedido == 1, Cliente.geometria.isnot(None)))
            .order_by(distancia)
            .limit(1)
            .first()
        )
        if row is None:
            return None

        pedido = API.to_dict(row)
        if pedido.get("distancia") is not None:
            pedido["distancia"] = int(round(pedido["distancia"]))
        hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        pedido_fecha = (
            session.query(Pedido.id_pedido, Pedido.fecha)
            .filter(Pedido.id_cliente == row.id, Pedido.fecha >= hoy)
            .order_by(Pedido.fecha.asc(), Pedido.id_pedido.asc())
            .first()
        )
        if pedido_fecha is None:
            pedido_fecha = (
                session.query(Pedido.id_pedido, Pedido.fecha)
                .filter(Pedido.id_cliente == row.id)
                .order_by(Pedido.fecha.desc(), Pedido.id_pedido.desc())
                .first()
            )
        if pedido_fecha is not None:
            pedido["id_pedido"] = pedido_fecha.id_pedido
            fecha = pedido_fecha.fecha
            pedido["fecha"] = fecha.date().isoformat() if isinstance(fecha, datetime.datetime) else fecha.isoformat()
        else:
            pedido["id_pedido"] = None
            pedido["fecha"] = None
        pedido["observaciones"] = pedido.pop("observacion", None)
        return pedido

    DISTANCIA_MAXIMA_RED = 300

    @staticmethod
    def calcularRuta(session, origen, destino):
        """
        Recorrido más corto en metros entre dos puntos EPSG:4326 sobre el callejero,
        sin recorrer tramos a contramano. Cada punto se conecta al punto más cercano
        de su tramo y los tramos extremos se recortan.
        Retorna (resultado, datos): 'success', 'out_of_network' o 'not_found'.
        """
        punto_sql = "ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 5347)"
        tramo_sql = text(f"""
            SELECT id, ST_Distance(the_geom, {punto_sql}) AS distancia,
                   ST_LineLocatePoint(the_geom, {punto_sql}) AS fraccion
            FROM {schema}.callejero
            WHERE source IS NOT NULL AND target IS NOT NULL
            ORDER BY the_geom <-> {punto_sql}
            LIMIT 1
        """)
        tramos = {}
        for rol, punto in (("origen", origen), ("destino", destino)):
            tramo = session.execute(tramo_sql, {"lon": punto["longitud"], "lat": punto["latitud"]}).first()
            if tramo is None or tramo.distancia > API.DISTANCIA_MAXIMA_RED:
                return "out_of_network", {
                    "error": f"El {rol} está a más de {API.DISTANCIA_MAXIMA_RED} m del callejero."
                }
            tramos[rol] = (int(tramo.id), float(tramo.fraccion))

        (tramo_o, fraccion_o), (tramo_d, fraccion_d) = tramos["origen"], tramos["destino"]
        # pgRouting descarta las aristas con costo negativo: así se respeta el sentido.
        aristas_sql = f"""
            SELECT id, source, target,
                   CASE WHEN sentido = 1 THEN -1 ELSE ST_Length(the_geom) END AS cost,
                   CASE WHEN sentido = 0 THEN -1 ELSE ST_Length(the_geom) END AS reverse_cost
            FROM {schema}.callejero
            WHERE source IS NOT NULL AND target IS NOT NULL
        """
        puntos_sql = (
            f"SELECT 1 AS pid, {tramo_o} AS edge_id, {fraccion_o!r}::float AS fraction "
            f"UNION ALL SELECT 2, {tramo_d}, {fraccion_d!r}::float"
        )
        # Los puntos de pgr_withPoints son nodos con id negativo: -1 origen, -2 destino.
        fila = session.execute(text(f"""
            WITH ruta AS (
                SELECT seq, node, edge, LEAD(node) OVER (ORDER BY seq) AS siguiente
                FROM public.pgr_withPoints(CAST(:aristas AS text), CAST(:puntos AS text), -1, -2,
                                           directed := true, driving_side := 'b')
            ),
            tramos AS (
                SELECT r.seq AS orden, c.the_geom AS geom,
                       CASE WHEN r.node = -1 THEN :f_o WHEN r.node = -2 THEN :f_d
                            WHEN r.node = c.source THEN 0.0 ELSE 1.0 END AS desde,
                       CASE WHEN r.siguiente = -1 THEN :f_o WHEN r.siguiente = -2 THEN :f_d
                            WHEN r.siguiente = c.source THEN 0.0 ELSE 1.0 END AS hasta
                FROM ruta r
                JOIN {schema}.callejero c ON c.id = r.edge
            ),
            partes AS (
                SELECT 0 AS orden, ST_Transform(ST_SetSRID(ST_MakePoint(:lon_o, :lat_o), 4326), 5347) AS geom
                UNION ALL
                SELECT orden, CASE WHEN desde <= hasta THEN ST_LineSubstring(geom, desde, hasta)
                                   ELSE ST_Reverse(ST_LineSubstring(geom, hasta, desde)) END
                FROM tramos
                UNION ALL SELECT 2147483647, ST_Transform(ST_SetSRID(ST_MakePoint(:lon_d, :lat_d), 4326), 5347)
            ),
            linea AS (SELECT ST_MakeLine(geom ORDER BY orden) AS geom FROM partes)
            SELECT (SELECT count(*) FROM tramos) AS cantidad,
                   ST_Length(geom) AS distancia,
                   ST_AsGeoJSON(ST_Transform(geom, 4326)) AS geojson
            FROM linea
        """), {
            "aristas": aristas_sql,
            "puntos": puntos_sql,
            "f_o": fraccion_o, "f_d": fraccion_d,
            "lon_o": origen["longitud"], "lat_o": origen["latitud"],
            "lon_d": destino["longitud"], "lat_d": destino["latitud"],
        }).first()

        mismo_lugar = tramo_o == tramo_d and abs(fraccion_o - fraccion_d) < 1e-9
        if fila.cantidad == 0 and not mismo_lugar:
            return "not_found", {"error": "No hay recorrido posible entre los puntos elegidos."}
        return "success", {
            "geometria": json.loads(fila.geojson),
            "distancia_m": int(round(fila.distancia)),
            "tramos": int(fila.cantidad),
        }

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
                Pedido.fecha,
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
        Elimina el pedido.
        Si el cliente conserva otro pedido de hoy o posterior, tiene_pedido sigue en 1.
        """
        pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).one_or_none()
        if pedido is None:
            return "not_found", "Pedido no encontrado."

        id_cliente = pedido.id_cliente
        hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        conserva_pedido = False
        if id_cliente is not None:
            conserva_pedido = session.query(Pedido.id_pedido).filter(
                Pedido.id_cliente == id_cliente,
                Pedido.id_pedido != id_pedido,
                Pedido.fecha >= hoy,
            ).first() is not None

        session.delete(pedido)
        if id_cliente is not None and not conserva_pedido:
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
    def iniciarPedidos(session):
        """
        Deja sin pedido activo a los clientes que tienen uno.
        No borra filas de la tabla pedido.
        """
        actualizados = (
            session.query(Cliente)
            .filter(Cliente.tiene_pedido == 1)
            .update(
                {
                    "tiene_pedido": 0,
                    "cantidad": 1,
                    "horario": None,
                    "nro_pao": None,
                    "es_regalo": 0,
                },
                synchronize_session=False,
            )
        )
        session.flush()
        if actualizados:
            return "success", f"Se iniciaron los pedidos. {actualizados} clientes quedaron sin pedido activo."
        return "success", "No había clientes con pedido activo."

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