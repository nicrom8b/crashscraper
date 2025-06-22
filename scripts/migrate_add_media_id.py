#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar la columna media_id
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import engine, Base, Noticia
from sqlalchemy import text

def migrate_add_media_id():
    """Agrega la columna media_id a la tabla noticias"""
    
    print("🔄 Migrando base de datos para agregar columna media_id...")
    
    try:
        # Verificar si la columna ya existe
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'noticias' 
                AND COLUMN_NAME = 'media_id'
            """))
            
            if result.fetchone():
                print("✅ La columna media_id ya existe")
                return
            
            # Agregar la columna media_id
            print("📝 Agregando columna media_id...")
            conn.execute(text("""
                ALTER TABLE noticias 
                ADD COLUMN media_id VARCHAR(50) NULL
            """))
            conn.commit()
            
            print("✅ Columna media_id agregada exitosamente")
            
            # Actualizar registros existentes con valores por defecto
            print("🔄 Actualizando registros existentes...")
            
            # Para Pregón (basado en URLs que contengan 'pregon.com.ar')
            conn.execute(text("""
                UPDATE noticias 
                SET media_id = 'pregon' 
                WHERE url LIKE '%pregon.com.ar%'
            """))
            
            # Para Jujuy al Momento
            conn.execute(text("""
                UPDATE noticias 
                SET media_id = 'jujuyalmomento' 
                WHERE url LIKE '%jujuyalmomento.com%'
            """))
            
            # Para Jujuy Dice
            conn.execute(text("""
                UPDATE noticias 
                SET media_id = 'jujuydice' 
                WHERE url LIKE '%jujuydice.com%'
            """))
            
            conn.commit()
            
            # Mostrar estadísticas
            result = conn.execute(text("""
                SELECT media_id, COUNT(*) as count 
                FROM noticias 
                WHERE media_id IS NOT NULL 
                GROUP BY media_id
            """))
            
            print("📊 Estadísticas de noticias por medio:")
            for row in result:
                print(f"   📰 {row.media_id}: {row.count} noticias")
            
            # Contar noticias sin media_id
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM noticias 
                WHERE media_id IS NULL
            """))
            
            sin_media_id = result.fetchone().count
            if sin_media_id > 0:
                print(f"   ⚠️ {sin_media_id} noticias sin media_id asignado")
            
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_add_media_id() 