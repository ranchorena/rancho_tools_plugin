"""Mismas operaciones en /api (raweb) y en /api/v1 (contrato versionado)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.api.contratos import (
    ActualizarClienteIn,
    AgregarClienteIn,
    AgregarClienteOut,
    BuscarClientesIn,
    BuscarDireccionIn,
    BuscarDireccionOut,
    CalcularRutaIn,
    ClienteBusquedaOut,
    ClientePedidoOut,
    EliminarPedidoIn,
    ErrorOut,
    HistoricoOut,
    MensajeOut,
    PedidoCercanoRespuesta,
    PedidoDeFechaOut,
    RutaOut,
    SinPedidosOut,
)
from app.api.deps import RolEscritura, RolLectura, UowDep, identidad_actual
from app.application.clientes.actualizar_cliente import actualizar_cliente
from app.application.clientes.agregar_cliente import agregar_cliente
from app.application.clientes.buscar_clientes import buscar_clientes
from app.application.direcciones.buscar_direccion import buscar_direccion
from app.application.pedidos.eliminar_pedido import eliminar_pedido
from app.application.pedidos.iniciar_pedidos import iniciar_pedidos
from app.application.pedidos.listar_con_pedido import listar_clientes_con_pedido
from app.application.pedidos.listar_historico import listar_historico
from app.application.pedidos.obtener_pedido_cercano import obtener_pedido_cercano
from app.application.pedidos.obtener_pedido_de_fecha import obtener_pedido_de_fecha
from app.application.rutas.calcular_ruta import calcular_ruta
from app.infrastructure.unit_of_work import UnitOfWork

_ERRORES = {
    400: {"model": ErrorOut},
    401: {"model": ErrorOut},
    403: {"model": ErrorOut},
    404: {"model": ErrorOut},
    500: {"model": ErrorOut},
}


def construir_router(version: str) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/direcciones/buscar",
        operation_id=f"buscar_direccion_{version}",
        tags=["Direcciones"],
        summary="Busca una dirección y devuelve el centroide del tramo",
        response_model=BuscarDireccionOut,
        responses=_ERRORES,
    )
    def post_buscar_direccion(datos: BuscarDireccionIn, uow: UnitOfWork = UowDep):
        return buscar_direccion(uow, datos.model_dump(exclude_unset=True))

    @router.post(
        "/clientes/buscar",
        operation_id=f"buscar_clientes_{version}",
        tags=["Clientes"],
        summary="Busca clientes por nombre, dirección o calle y altura",
        response_model=list[ClienteBusquedaOut],
        responses=_ERRORES,
    )
    def post_buscar_clientes(
        datos: BuscarClientesIn,
        uow: UnitOfWork = UowDep,
        _identidad: dict = RolLectura,
    ):
        return buscar_clientes(uow, datos.model_dump(exclude_unset=True))

    @router.put(
        "/clientes/actualizar/{cliente_id}",
        operation_id=f"actualizar_cliente_{version}",
        tags=["Clientes"],
        summary="Actualiza un cliente y registra o actualiza su pedido",
        response_model=MensajeOut,
        responses=_ERRORES,
    )
    def put_actualizar_cliente(
        cliente_id: int,
        datos: ActualizarClienteIn,
        request: Request,
        uow: UnitOfWork = UowDep,
        _identidad: dict = RolEscritura,
    ):
        return actualizar_cliente(uow, cliente_id, datos.model_dump(exclude_unset=True), identidad_actual(request))

    @router.post(
        "/clientes/agregar",
        operation_id=f"agregar_cliente_{version}",
        tags=["Clientes"],
        summary="Agrega un cliente",
        response_model=AgregarClienteOut,
        status_code=201,
        responses=_ERRORES,
    )
    def post_agregar_cliente(datos: AgregarClienteIn, uow: UnitOfWork = UowDep):
        return agregar_cliente(uow, datos.model_dump(exclude_unset=True))

    @router.get(
        "/clientes/pedidos",
        operation_id=f"listar_clientes_con_pedido_{version}",
        tags=["Clientes"],
        summary="Lista los clientes con pedido activo",
        response_model=list[ClientePedidoOut] | SinPedidosOut,
        responses=_ERRORES,
    )
    def get_clientes_con_pedido(uow: UnitOfWork = UowDep, _identidad: dict = RolLectura):
        return listar_clientes_con_pedido(uow)

    @router.get(
        "/clientes/{cliente_id}/pedido",
        operation_id=f"obtener_pedido_de_fecha_{version}",
        tags=["Pedidos"],
        summary="Devuelve el pedido del cliente para una fecha",
        response_model=PedidoDeFechaOut,
        responses=_ERRORES,
    )
    def get_pedido_de_fecha(
        cliente_id: int,
        fecha: str | None = None,
        uow: UnitOfWork = UowDep,
        _identidad: dict = RolLectura,
    ):
        return obtener_pedido_de_fecha(uow, cliente_id, fecha)

    @router.get(
        "/pedidos/cercano",
        operation_id=f"obtener_pedido_cercano_{version}",
        tags=["Pedidos"],
        summary="Devuelve el pedido activo de menor recorrido",
        response_model=PedidoCercanoRespuesta,
        response_model_exclude_unset=True,
        responses=_ERRORES,
    )
    def get_pedido_cercano(
        latitud: str | None = None,
        longitud: str | None = None,
        uow: UnitOfWork = UowDep,
        _identidad: dict = RolLectura,
    ):
        return obtener_pedido_cercano(uow, latitud, longitud)

    @router.post(
        "/rutas/calcular",
        operation_id=f"calcular_ruta_{version}",
        tags=["Rutas"],
        summary="Calcula el recorrido más corto entre dos puntos",
        response_model=RutaOut,
        responses=_ERRORES,
    )
    def post_calcular_ruta(datos: CalcularRutaIn, uow: UnitOfWork = UowDep):
        return calcular_ruta(uow, datos.model_dump(exclude_unset=True))

    @router.get(
        "/pedidos/historico",
        operation_id=f"listar_historico_{version}",
        tags=["Pedidos"],
        summary="Lista los pedidos entre dos fechas",
        response_model=HistoricoOut,
        responses=_ERRORES,
    )
    def get_historico(
        desde: str | None = None,
        hasta: str | None = None,
        uow: UnitOfWork = UowDep,
        _identidad: dict = RolLectura,
    ):
        return listar_historico(uow, desde, hasta)

    @router.post(
        "/pedidos/eliminar",
        operation_id=f"eliminar_pedido_{version}",
        tags=["Pedidos"],
        summary="Elimina un pedido",
        response_model=MensajeOut,
        responses=_ERRORES,
    )
    def post_eliminar_pedido(
        datos: EliminarPedidoIn,
        uow: UnitOfWork = UowDep,
        _identidad: dict = RolEscritura,
    ):
        return eliminar_pedido(uow, datos.model_dump(exclude_unset=True))

    @router.post(
        "/pedidos/iniciar",
        operation_id=f"iniciar_pedidos_{version}",
        tags=["Pedidos"],
        summary="Deja sin pedido activo a los clientes",
        response_model=MensajeOut,
        responses=_ERRORES,
    )
    def post_iniciar_pedidos(uow: UnitOfWork = UowDep, _identidad: dict = RolEscritura):
        return iniciar_pedidos(uow)

    return router
