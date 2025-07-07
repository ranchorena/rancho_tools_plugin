# raapi/API.py
# coding=utf-8

from sqlalchemy import text
from decimal import Decimal

class API: # Clase contenedora renombrada a API
    @staticmethod
    def to_dict(row):
        """Convierte una fila de SQLAlchemy (o similar con ._mapping) a un diccionario."""
        if row is None:
            return None
        if hasattr(row, '_mapping'):
            return dict(row._mapping)
        return {key: value for key, value in row.items()}

    @staticmethod
    def buscar_cliente_por_nombre(session, nombre_cliente):
        """
        Busca clientes donde el campo nombre contenga nombre_cliente (insensible a mayúsculas/minúsculas).
        Retorna una lista de diccionarios de cliente con Id, Nombre, Direccion, Calle, Altura.
        """
        query = text("""
            SELECT id, nombre, direccion, calle, altura
            FROM generalbelgrano.clientes
            WHERE lower(nombre) LIKE lower(:nombre_cliente)
        """)
        result = session.execute(query, {"nombre_cliente": f"%{nombre_cliente}%"})
        clientes = [API.to_dict(row) for row in result.fetchall()]
        return clientes

    @staticmethod
    def buscar_clientes_por_direccion(session, direccion_buscada):
        """
        Busca clientes donde el campo direccion contenga direccion_buscada (insensible a mayúsculas/minúsculas).
        Retorna una lista de diccionarios de cliente con Id, Nombre, Direccion, Calle, Altura.
        """
        query = text("""
            SELECT id, nombre, direccion, calle, altura
            FROM generalbelgrano.clientes
            WHERE lower(direccion) LIKE lower(:direccion)
        """)
        result = session.execute(query, {"direccion": f"%{direccion_buscada}%"})
        clientes = [API.to_dict(row) for row in result.fetchall()]
        return clientes

    @staticmethod
    def buscar_clientes_por_calle_altura(session, calle_buscada, altura_buscada=None):
        """
        Busca clientes donde el campo calle contenga calle_buscada (insensible a mayúsculas/minúsculas).
        Si altura_buscada se proporciona, también filtra por altura.
        Retorna una lista de diccionarios de cliente con Id, Nombre, Direccion, Calle, Altura.
        """
        sql_query_str = """
            SELECT id, nombre, direccion, calle, altura
            FROM generalbelgrano.clientes
            WHERE lower(calle) LIKE lower(:calle_param)
        """
        params = {"calle_param": f"%{calle_buscada}%"}

        if altura_buscada is not None:
            try:
                altura_int = int(altura_buscada)
                sql_query_str += " AND altura = :altura_param"
                params["altura_param"] = altura_int
            except ValueError:
                pass

        query = text(sql_query_str)
        result = session.execute(query, params)
        clientes = [API.to_dict(row) for row in result.fetchall()]
        return clientes

    @staticmethod
    def actualizar_cliente(session, cliente_id, datos_actualizados):
        """
        Actualiza los campos docenas (cantidad), nro_pao, tiene_pedido, es_regalo,
        observaciones (observacion), y horario para el cliente con cliente_id.
        Retorna True si la actualización fue exitosa, False en caso contrario.
        """
        mapa_campos = {
            "docenas": "cantidad",
            "nro_pao": "nro_pao",
            "tiene_pedido": "tiene_pedido",
            "es_regalo": "es_regalo",
            "observaciones": "observacion",
            "horario": "horario"
        }

        set_clauses = []
        params_update = {"cliente_id": cliente_id}

        for key_dto, value_dto in datos_actualizados.items():
            db_column_name = mapa_campos.get(key_dto)
            if db_column_name:
                if key_dto in ["tiene_pedido", "es_regalo"]:
                    params_update[db_column_name] = 1 if value_dto else 0
                elif key_dto == "horario":
                    params_update[db_column_name] = value_dto if value_dto else None
                elif key_dto == "docenas":
                    params_update[db_column_name] = float(value_dto) if value_dto is not None else None
                elif key_dto == "nro_pao":
                     params_update[db_column_name] = int(value_dto) if value_dto is not None else None
                else:
                    params_update[db_column_name] = value_dto

                set_clauses.append(f"{db_column_name} = :{db_column_name}")

        if not set_clauses:
            return False

        sql_update_query_str = f"""
            UPDATE generalbelgrano.clientes
            SET {', '.join(set_clauses)}
            WHERE id = :cliente_id
        """

        try:
            result = session.execute(text(sql_update_query_str), params_update)
            if result.rowcount > 0:
                session.commit()
                return True
            else:
                session.rollback()
                return False
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar cliente: {e}")
            return False

    @staticmethod
    def getClienteById(session, cliente_id):
        """
        Obtiene un cliente específico por su ID.
        Retorna un diccionario con todos los datos del cliente o None si no existe.
        """
        query = text("""
            SELECT id, nombre, direccion, calle, altura, cantidad, nro_pao, 
                   tiene_pedido, es_regalo, observacion, horario
            FROM generalbelgrano.clientes
            WHERE id = :cliente_id
        """)
        result = session.execute(query, {"cliente_id": cliente_id})
        row = result.fetchone()
        return API.to_dict(row) if row else None
