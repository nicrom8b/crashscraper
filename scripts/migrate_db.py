#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar los campos de clasificadores.
"""

import sys
import os

# Agregar el directorio app al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db import engine, Base, SessionLocal
from sqlalchemy import text

def migrate_database():
    """Ejecuta la migración para agregar los campos de clasificadores"""
    print("🔄 Iniciando migración de base de datos...")
    
    try:
        # Crear las tablas si no existen
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas/verificadas")
        
        # Verificar si los campos ya existen
        db = SessionLocal()
        
        # Verificar si los campos de clasificadores existen
        result = db.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'noticias' 
            AND COLUMN_NAME IN ('es_accidente_simple', 'es_accidente_stem', 'es_accidente_lemma', 'es_accidente_ml')
        """))
        
        existing_columns = [row[0] for row in result.fetchall()]
        missing_columns = []
        
        required_columns = ['es_accidente_simple', 'es_accidente_stem', 'es_accidente_lemma', 'es_accidente_ml']
        
        for column in required_columns:
            if column not in existing_columns:
                missing_columns.append(column)
        
        if not missing_columns:
            print("✅ Todos los campos de clasificadores ya existen")
            db.close()
            return True
        
        print(f"📝 Agregando campos faltantes: {missing_columns}")
        
        # Agregar campos faltantes
        for column in missing_columns:
            try:
                db.execute(text(f"ALTER TABLE noticias ADD COLUMN {column} BOOLEAN DEFAULT NULL"))
                print(f"  ✅ Agregado campo: {column}")
            except Exception as e:
                print(f"  ❌ Error agregando {column}: {e}")
        
        db.commit()
        print("✅ Migración completada exitosamente")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        return False

if __name__ == "__main__":
    if migrate_database():
        print("🎉 Base de datos migrada correctamente")
    else:
        print("💥 Error en la migración")
        sys.exit(1) 