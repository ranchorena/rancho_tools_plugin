"""Actualiza un cliente y, si tiene pedido, inserta o actualiza el pedido de esa fecha."""

from __future__ import annotations

import datetime
import logging

from app.application.clientes.conversiones import como_horario
from app.application.comun import ejecutar
from app.domain.direcciones.parser import parse_direccion
from app.domain.errors import DomainError
from app.domain.geo.coordenadas import punto_pedido
from app.domain.pedidos.fechas import fecha_pedido
from app.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger("ra_ng_api")

_MAPA_CAMPOS = {
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


def actualizar_cliente(uow: UnitOfWork, cliente_id: int, datos: dict, identidad: dict | None) -> dict:
    def operacion() -> dict:
        if not datos:
            raise DomainError(400, "No se proporcionaron datos para actualizar.")
        filtrados = {clave: valor for clave, valor in datos.items() if clave in _MAPA_CAMPOS}
        if not filtrados:
            raise DomainError(400, "No se proporcionaron campos válidos para actualizar.")
        if not uow.clientes.existe(cliente_id):
            raise DomainError(404, f"Cliente con ID {cliente_id} no encontrado.")

        valores: dict = {}
        for clave, valor in filtrados.items():
            columna = _MAPA_CAMPOS[clave]
            if clave in ("tiene_pedido", "es_regalo"):
                valores[columna] = 1 if valor else 0
            elif clave == "horario":
                valores[columna] = como_horario(valor)
            elif clave == "docenas":
                valores[columna] = float(valor) if valor is not None else None
            elif clave == "nro_pao":
                valores[columna] = int(valor) if valor is not None else None
            elif clave == "direccion":
                texto = str(valor).strip() if valor is not None else ""
                if not texto:
                    raise DomainError(400, "La dirección del cliente es requerida.")
                valores[columna] = texto
            elif clave == "altura":
                if valor in (None, ""):
                    valores[columna] = None
                else:
                    try:
                        valores[columna] = int(valor)
                    except (TypeError, ValueError) as error:
                        raise DomainError(400, "La altura no es válida.") from error
            elif clave in ("calle", "telefono"):
                texto = str(valor).strip() if valor is not None else ""
                valores[columna] = texto or None
            else:
                valores[columna] = valor

        datos_pedido = None
        if valores.get("tiene_pedido") == 1:
            fecha = fecha_pedido(datos)
            if fecha is None:
                raise DomainError(400, "La fecha del pedido no es válida.")
            precio = uow.precios.vigente()
            if precio is None:
                raise DomainError(400, "No hay un precio vigente para registrar el pedido.")
            cliente = uow.clientes.obtener(cliente_id)
            direccion_pedido = datos.get("direccion_pedido")
            if isinstance(direccion_pedido, str):
                direccion_pedido = direccion_pedido.strip() or None
            else:
                direccion_pedido = None
            calle_pedido, altura_pedido = (None, None)
            if direccion_pedido:
                calle_pedido, altura_pedido = parse_direccion(direccion_pedido)
            try:
                punto = punto_pedido(datos)
            except ValueError as error:
                raise DomainError(400, str(error)) from error
            datos_pedido = {
                "fecha": datetime.datetime.combine(fecha, datetime.time.min),
                "id_cliente": cliente_id,
                "nombre": cliente.nombre,
                "turno": 1,
                "cantidad": valores["cantidad"] if "cantidad" in valores and valores["cantidad"] is not None else cliente.cantidad,
                "direccion": direccion_pedido or cliente.direccion,
                "calle": calle_pedido or cliente.calle,
                "altura": altura_pedido if altura_pedido is not None else cliente.altura,
                "observaciones": valores.get("observacion", cliente.observacion),
                "precio_unitario": precio,
                "nro_pao": valores.get("nro_pao", cliente.nro_pao),
            }
            if punto is None:
                datos_pedido["geometry"] = cliente.geometria
            else:
                datos_pedido["lon"] = float(datos["longitud"])
                datos_pedido["lat"] = float(datos["latitud"])

        if uow.clientes.actualizar(cliente_id, valores) <= 0:
            raise DomainError(400, "No se pudo actualizar el cliente.")
        if datos_pedido is not None:
            mensaje = uow.pedidos.guardar(datos_pedido)
        else:
            mensaje = "Cliente actualizado correctamente."
        if datos.get("tiene_pedido"):
            quien = identidad or {}
            logger.info(
                "pedido registrado cliente_id=%s sub=%s preferred_username=%s email=%s",
                cliente_id,
                quien.get("sub"),
                quien.get("preferred_username"),
                quien.get("email"),
            )
        return {"mensaje": mensaje}

    return ejecutar(uow, operacion, "Error interno del servidor al actualizar el cliente.")
