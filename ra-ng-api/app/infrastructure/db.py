"""Motor y sesiones SQLAlchemy 2. La conexión se abre al usar la sesión, no al importar."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
