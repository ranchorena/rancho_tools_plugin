"""Columnas que la API lee y escribe. El schema sale de DB_SCHEMA."""

from __future__ import annotations

import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Date, DateTime, Float, Integer, Numeric, String, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

SCHEMA = settings.db_schema


class Base(DeclarativeBase):
    pass


class Cliente(Base):
    __tablename__ = "clientes"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geometria = mapped_column(Geometry(geometry_type="POINT", srid=5347), nullable=True)
    nombre: Mapped[str | None] = mapped_column(String(60))
    direccion: Mapped[str | None] = mapped_column(String(50))
    calle: Mapped[str | None] = mapped_column(String(50))
    altura: Mapped[int | None] = mapped_column(Integer)
    tiene_pedido: Mapped[int | None] = mapped_column(Integer)
    telefono: Mapped[str | None] = mapped_column(String(30))
    cantidad: Mapped[float | None] = mapped_column(Float)
    horario: Mapped[datetime.time | None] = mapped_column(Time)
    nro_pao: Mapped[int | None] = mapped_column(Integer)
    observacion: Mapped[str | None] = mapped_column(String(200))
    es_regalo: Mapped[int | None] = mapped_column(Integer)


class Pedido(Base):
    __tablename__ = "pedido"
    __table_args__ = {"schema": SCHEMA}

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[datetime.datetime] = mapped_column(DateTime)
    id_cliente: Mapped[int] = mapped_column(BigInteger)
    nombre: Mapped[str | None] = mapped_column(String(60))
    turno: Mapped[int] = mapped_column(Integer)
    cantidad: Mapped[float | None] = mapped_column(Float)
    direccion: Mapped[str | None] = mapped_column(String(50))
    calle: Mapped[str | None] = mapped_column(String(50))
    altura: Mapped[int | None] = mapped_column(Integer)
    geometry = mapped_column(Geometry(geometry_type="POINT", srid=5347), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(String(30))
    precio_unitario: Mapped[float | None] = mapped_column(Float)
    nro_pao: Mapped[int | None] = mapped_column(Integer)


class Precio(Base):
    __tablename__ = "precio"
    __table_args__ = {"schema": SCHEMA}

    id_precio: Mapped[int] = mapped_column(Integer, primary_key=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    fecha: Mapped[datetime.date] = mapped_column(Date)


class Tramo(Base):
    __tablename__ = "tramos"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geometry = mapped_column(Geometry(geometry_type="MULTILINESTRING", srid=5347), nullable=True)
    calle: Mapped[str | None] = mapped_column(String(60))
    desde: Mapped[int | None] = mapped_column(BigInteger)
    hasta: Mapped[int | None] = mapped_column(BigInteger)
