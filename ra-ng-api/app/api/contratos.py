"""Cuerpos JSON del contrato. Los nombres de alta y de actualización no se unifican."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorOut(BaseModel):
    error: str


class BuscarDireccionIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    direccion: str = Field(examples=["SARMIENTO 550"])


class BuscarClientesIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    criterio: str = Field(examples=["nombre"])
    nombre_cliente: str | None = None
    direccion: str | None = None
    calle: str | None = None
    altura: Any = None


class ActualizarClienteIn(BaseModel):
    """`docenas` se guarda en cantidad y `observaciones` en observacion."""

    model_config = ConfigDict(extra="ignore")
    docenas: Any = None
    nro_pao: Any = None
    tiene_pedido: Any = None
    es_regalo: Any = None
    observaciones: str | None = None
    horario: str | None = None
    fecha: str | None = None
    direccion: str | None = None
    calle: str | None = None
    altura: Any = None
    telefono: str | None = None
    direccion_pedido: str | None = None
    latitud: Any = None
    longitud: Any = None


class AgregarClienteIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nombre: str
    direccion: str
    latitud: Any
    longitud: Any
    calle: str | None = None
    altura: Any = None
    telefono: str | None = None
    tiene_pedido: Any = None
    cantidad: Any = None
    horario: str | None = None
    fecha: str | None = None
    nro_pao: Any = None
    observacion: str | None = None
    es_regalo: Any = None


class PuntoIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    latitud: Any = None
    longitud: Any = None


class CalcularRutaIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    origen: PuntoIn | None = None
    destino: PuntoIn | None = None


class EliminarPedidoIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id_pedido: Any = None


class MensajeOut(BaseModel):
    mensaje: str


class ClienteCreadoOut(BaseModel):
    id: int
    nombre: str | None = None
    direccion: str | None = None
    calle: str | None = None
    altura: int | None = None
    longitud: float | None = None
    latitud: float | None = None


class AgregarClienteOut(BaseModel):
    mensaje: str
    cliente: ClienteCreadoOut


class TramoInfoOut(BaseModel):
    id: int
    nombre_calle: str | None = None
    desde: int | None = None
    hasta: int | None = None


class BuscarDireccionOut(BaseModel):
    latitud: float
    longitud: float
    tramo_info: TramoInfoOut


class ClienteBusquedaOut(BaseModel):
    id: int
    nombre: str | None = None
    direccion: str | None = None
    calle: str | None = None
    altura: int | None = None
    telefono: str | None = None
    tiene_pedido: int | None = None
    longitud: float | None = None
    latitud: float | None = None


class ClientePedidoOut(BaseModel):
    id: int
    nombre: str | None = None
    direccion: str | None = None
    calle: str | None = None
    altura: int | None = None
    tiene_pedido: int | None = None
    telefono: str | None = None
    cantidad: float | None = None
    horario: str | None = None
    nro_pao: int | None = None
    observacion: str | None = None
    es_regalo: int | None = None
    longitud: float | None = None
    latitud: float | None = None


class SinPedidosOut(BaseModel):
    message: str


class PedidoFechaOut(BaseModel):
    id: int | None = None
    fecha: str | None = None
    cantidad: float | None = None
    direccion: str | None = None
    calle: str | None = None
    altura: int | None = None
    nro_pao: int | None = None
    observacion: str | None = None
    longitud: float | None = None
    latitud: float | None = None


class PedidoDeFechaOut(BaseModel):
    pedido: PedidoFechaOut | None = None


class RutaOut(BaseModel):
    geometria: dict[str, Any]
    distancia_m: int
    tramos: int


class PedidoCercanoOut(BaseModel):
    id: int | None = None
    nombre: str | None = None
    direccion: str | None = None
    calle: str | None = None
    altura: int | None = None
    telefono: str | None = None
    cantidad: float | None = None
    horario: str | None = None
    longitud: float | None = None
    latitud: float | None = None
    distancia: int | None = None
    id_pedido: int | None = None
    fecha: str | None = None
    observaciones: str | None = None


class PedidoCercanoRespuesta(BaseModel):
    pedido: PedidoCercanoOut | None = None
    ruta: RutaOut | None = None


class PedidoHistoricoOut(BaseModel):
    id: int
    fecha: str | None = None
    id_cliente: int | None = None
    nombre: str | None = None
    direccion: str | None = None
    cantidad: float | None = None
    telefono: str | None = None
    horario: str | None = None
    nro_pao: int | None = None
    es_regalo: int | None = None
    precio_unitario: float | None = None
    observacion: str | None = None
    longitud: float | None = None
    latitud: float | None = None


class HistoricoOut(BaseModel):
    fecha_desde: str | None = None
    fecha_hasta: str | None = None
    pedidos: list[PedidoHistoricoOut]
