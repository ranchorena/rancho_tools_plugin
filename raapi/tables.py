from sqlalchemy import Table, Column, String, MetaData, Integer, Numeric, ForeignKey, PrimaryKeyConstraint, DateTime, Boolean, and_
from sqlalchemy.sql import null
from config import *
from sqlalchemy.orm import relationship, foreign

# Tabla Barrios
class Barrio(Base):
    __table__ = Table('barrios', Base.metadata, autoload_with=engine, schema=schema)

# # Tabla Callejero (Sin clave primaria - comentada)
# class Callejero(Base):
#     __table__ = Table('callejero', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Callejero Vertices PGR
class CallejeroVerticesPgr(Base):
    __table__ = Table('callejero_vertices_pgr', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Calles Nombres
class CallesNombres(Base):
    __table__ = Table('calles_nombres', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Clientes
class Cliente(Base):
    __table__ = Table('clientes', Base.metadata, autoload_with=engine, schema=schema)

# # Tabla Clientes Temporal (Sin clave primaria - comentada)
# class ClienteTemporal(Base):
#     __table__ = Table('clientes_temporal', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Fracciones
class Fraccion(Base):
    __table__ = Table('fracciones', Base.metadata, autoload_with=engine, schema=schema)

# # Tabla Partido (Sin clave primaria - comentada)
# class Partido(Base):
#     __table__ = Table('partido', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Pedido
class Pedido(Base):
    __table__ = Table('pedido', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Plazas
class Plaza(Base):
    __table__ = Table('plazas', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Provincia
class Provincia(Base):
    __table__ = Table('provincia', Base.metadata, autoload_with=engine, schema=schema)

# # Tabla Provincia Polyg (Sin clave primaria - comentada)
# class ProvinciaPolyg(Base):
#     __table__ = Table('provincia_polyg', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Punto Interes
class PuntoInteres(Base):
    __table__ = Table('punto_interes', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Radios Censales
class RadioCensal(Base):
    __table__ = Table('radios_censales', Base.metadata, autoload_with=engine, schema=schema)

# # Tabla Referencia (Sin clave primaria - comentada)
# class Referencia(Base):
#     __table__ = Table('referencia', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Subbarrios
class Subbarrio(Base):
    __table__ = Table('subbarrios', Base.metadata, autoload_with=engine, schema=schema)

# # Tabla Temp Zonas Reparto (Sin clave primaria - comentada)
# class TempZonaReparto(Base):
#     __table__ = Table('temp_zonas_reparto', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Tramos
class Tramo(Base):
    __table__ = Table('tramos', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Urbano
class Urbano(Base):
    __table__ = Table('urbano', Base.metadata, autoload_with=engine, schema=schema)

# Tabla Zonas Reparto
class ZonaReparto(Base):
    __table__ = Table('zonas_reparto', Base.metadata, autoload_with=engine, schema=schema)

