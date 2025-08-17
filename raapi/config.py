# raapi/config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configuración de la base de datos PostgreSQL
# Por favor, reemplaza con tus credenciales reales
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
# Detectar si estamos en Docker o desarrollo local
DB_HOST = os.environ.get('DB_HOST', 'localhost')
# Si no estamos en Docker (no hay /app o similar), forzar localhost
if DB_HOST == 'db' and not os.path.exists('/app'):
    DB_HOST = 'localhost'
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'postgres')

schema = os.environ.get('DB_SCHEMA', 'generalbelgrano')

# Log para debugging
print(f"DEBUG: Configuración de BD - HOST: {DB_HOST}, PORT: {DB_PORT}, USER: {DB_USER}, DB: {DB_NAME}")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Clave JWT
jwt_key = b'rMpZvM/xJLJVmolNwMe9PM1J2V3y4j48CYBESnBddwMfk4GKHt6mQcoCO7nRMrODfKSjfr5KGc9Tk44Nz/dRnwsJ/i3+Hmz5lGeXD9DO8ZeQLq0WZMcdvDRKbfTUv6Vohju3gdYz01D8s6lPuqkY+G'

# Configuración de la Sesión de SQLAlchemy
Session = SessionLocal
