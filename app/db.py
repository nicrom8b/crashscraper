from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Usar DATABASE_URL si está disponible, sino usar las variables individuales
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Ajuste para SQLAlchemy 2.0 si es necesario, pero la URL de docker-compose es la prioridad
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Este bloque ahora es solo para desarrollo local fuera de Docker
    print("ADVERTENCIA: No se encontró DATABASE_URL. Usando configuración local.")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "example")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "accidentes_craper")
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    noticias = relationship("Noticia", back_populates="media")

class Noticia(Base):
    __tablename__ = "noticias"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    contenido = Column(Text, nullable=False)
    fecha = Column(Date, nullable=False)
    url = Column(String(255), nullable=False)
    
    media_id = Column(Integer, ForeignKey("media.id"))
    media = relationship("Media", back_populates="noticias")

    # Columna de clasificación unificada (puede estar vacía si usamos la antigua)
    classification = Column(String(50), nullable=True) 
    
    # Columna de clasificación antigua (la usamos para leer datos existentes)
    es_accidente_transito = Column(Boolean, default=None, nullable=True)

    # Columnas para los resultados de cada clasificador individual
    es_accidente_simple = Column(Boolean, nullable=True)
    es_accidente_stem = Column(Boolean, nullable=True)
    es_accidente_lemma = Column(Boolean, nullable=True)
    es_accidente_ml = Column(Boolean, nullable=True)

    contenido_crudo = Column(Text, nullable=True)

def get_db():
    """Obtiene una sesión de la base de datos"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise 