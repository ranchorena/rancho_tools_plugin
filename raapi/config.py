# raapi/config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# DEV habitual en Windows: DB_HOST=localhost, DB_PORT=5432.
# Dentro del contenedor, Compose inyecta DB_HOST_DOCKER
# (host.docker.internal, o db si se activó el perfil standalone).
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
# Un proceso fuera del contenedor no resuelve el hostname db.
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

# Configuración de la Sesión de SQLAlchemy
Session = SessionLocal
