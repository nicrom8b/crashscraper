from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usar DATABASE_URL si está disponible, sino usar las variables individuales
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "example")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "accidentes_craper")
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Noticia(Base):
    __tablename__ = "noticias"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    contenido = Column(Text, nullable=False)
    fecha = Column(Date, nullable=False)
    url = Column(String(255), nullable=False)
    es_accidente_transito = Column(Boolean, default=None, nullable=True)
    contenido_crudo = Column(Text, nullable=True)
    media_id = Column(String(50), nullable=True)  # Campo para identificar el medio de comunicación
    
    # Campos para los clasificadores
    es_accidente_simple = Column(Boolean, default=None, nullable=True)
    es_accidente_stem = Column(Boolean, default=None, nullable=True)
    es_accidente_lemma = Column(Boolean, default=None, nullable=True)
    es_accidente_ml = Column(Boolean, default=None, nullable=True)

def get_db():
    """Obtiene una sesión de la base de datos"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise 