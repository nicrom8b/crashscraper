#!/usr/bin/env python3
"""
Script para inicializar la base de datos:
- Elimina y crea todas las tablas.
- Pre-pobla la tabla `media` con todos los scrapers disponibles.
- Agrega un par de noticias de ejemplo.
"""
import sys
import os
from datetime import date

# Añadir el directorio raíz del proyecto al path para resolver los imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import Base, engine, SessionLocal
from app.scrapers import SCRAPERS
from app.db import Media, Noticia

def init_db():
    # Eliminar todas las tablas existentes y luego crearlas
    print("⚠️  Eliminando todas las tablas existentes...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tablas eliminadas.")

    print("🚀 Creando todas las tablas nuevas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas.")

    # Crear una sesión para poblar los datos
    db = SessionLocal()
    try:
        # --- Poblar la tabla de medios ---
        print("📰 Poblando la tabla de medios...")
        
        # Instanciar cada scraper para obtener su media_name
        media_names = [ScraperClass().media_name for ScraperClass in SCRAPERS]
        
        for media_name in media_names:
            if not db.query(Media).filter_by(name=media_name).first():
                db_media = Media(name=media_name)
                db.add(db_media)
        
        db.commit()
        print(f"✅ Medios insertados: {', '.join(media_names)}")

        # --- Agregar noticias de ejemplo ---
        print("📝 Agregando noticias de ejemplo...")

        # Obtener el primer y segundo medio para usarlos en los ejemplos
        medio1 = db.query(Media).filter_by(name=media_names[0]).first()
        medio2 = db.query(Media).filter_by(name=media_names[1]).first()

        if medio1:
            noticia1 = Noticia(
                titulo="Ejemplo de Accidente: Choque en la avenida principal",
                contenido="Dos vehículos colisionaron esta mañana en la Av. Savio. Hubo heridos leves y demoras en el tránsito.",
                fecha=date.today(),
                url="https://example.com/noticia1",
                media_id=medio1.id,
                classification='ACCIDENTE'
            )
            db.add(noticia1)

        if medio2:
            noticia2 = Noticia(
                titulo="Ejemplo de No Accidente: El gobernador inauguró una nueva escuela",
                contenido="El gobernador de la provincia cortó la cinta en la nueva escuela primaria del barrio Alto Comedero.",
                fecha=date.today(),
                url="https://example.com/noticia2",
                media_id=medio2.id,
                classification='NO_ACCIDENTE'
            )
            db.add(noticia2)
        
        db.commit()
        print("✅ Noticias de ejemplo agregadas.")

    finally:
        db.close()

    print("🎉 Base de datos inicializada y poblada correctamente.")

if __name__ == "__main__":
    init_db() 