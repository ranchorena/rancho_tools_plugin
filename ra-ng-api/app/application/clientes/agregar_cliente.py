"""Alta de cliente. Las coordenadas llegan en EPSG:4326 y se guardan en EPSG:5347."""

from __future__ import annotations

import datetime

from app.application.clientes.conversiones import como_horario
from app.application.comun import ejecutar
from app.domain.errors import DomainError
from app.domain.pedidos.fechas import fecha_pedido
from app.infrastructure.persistence.models import Pedido
from app.infrastructure.unit_of_work import UnitOfWork


def agregar_cliente(uow: UnitOfWork, datos: dict) -> dict:
    def operacion() -> dict:
        try:
            if not datos or not datos.get("nombre"):
                raise DomainError(400, "El nombre del cliente es requerido.")
            if not datos.get("direccion"):
                raise DomainError(400, "La dirección del cliente es requerida.")
            if not datos.get("latitud") or not datos.get("longitud"):
                raise DomainError(400, "Las coordenadas (latitud y longitud) son requeridas.")

            registra_pedido = 1 if datos.get("tiene_pedido") else 0
            fecha = None
            precio = None
            if registra_pedido:
                fecha = fecha_pedido(datos)
                if fecha is None:
                    raise DomainError(400, "La fecha del pedido no es válida.")
                precio = uow.precios.vigente()
                if precio is None:
                    raise DomainError(400, "No hay un precio vigente para registrar el pedido.")

            nuevo = {
                "nombre": datos["nombre"].strip(),
                "direccion": datos["direccion"].strip(),
                "calle": datos.get("calle", "").strip() if datos.get("calle") else None,
                "altura": int(datos["altura"]) if datos.get("altura") and str(datos["altura"]).strip() else None,
                "tiene_pedido": 1 if datos.get("tiene_pedido") else 0,
                "telefono": datos.get("telefono", "").strip() if datos.get("telefono") else None,
                "cantidad": float(datos["cantidad"]) if datos.get("cantidad") else 0.0,
                "horario": como_horario(datos.get("horario")) if datos.get("horario") else None,
                "nro_pao": int(datos["nro_pao"]) if datos.get("nro_pao") and str(datos["nro_pao"]).strip() else None,
                "observacion": datos.get("observacion", "").strip() if datos.get("observacion") else None,
                "es_regalo": 1 if datos.get("es_regalo") else 0,
                "latitud": float(datos["latitud"]),
                "longitud": float(datos["longitud"]),
            }
        except DomainError:
            raise
        except ValueError as error:
            raise DomainError(400, f"Error en los datos proporcionados: {error}") from error

        creado = uow.clientes.insertar(nuevo)
        if not creado:
            raise DomainError(400, "No se pudo crear el cliente.")
        if registra_pedido:
            cliente = uow.clientes.obtener(creado["id"])
            uow.pedidos.agregar(
                Pedido(
                    fecha=datetime.datetime.combine(fecha, datetime.time.min),
                    id_cliente=cliente.id,
                    nombre=cliente.nombre,
                    turno=1,
                    cantidad=nuevo["cantidad"],
                    direccion=cliente.direccion,
                    calle=cliente.calle,
                    altura=cliente.altura,
                    geometry=cliente.geometria,
                    observaciones=nuevo["observacion"],
                    precio_unitario=precio,
                    nro_pao=nuevo["nro_pao"],
                )
            )
        return {"mensaje": "Cliente agregado correctamente.", "cliente": creado}

    return ejecutar(uow, operacion, "Error interno del servidor al agregar el cliente.")
