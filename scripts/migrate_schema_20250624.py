#!/usr/bin/env python3
"""
Script para migrar el esquema de la base de datos sin perder datos.
- Crea la tabla 'media'.
- Añade la columna 'classification' a 'noticias'.
- Modifica la columna 'media_id' para ser una FK a 'media'.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, engine
from sqlalchemy import text

def column_exists(connection, table_name, column_name):
    """Verifica si una columna existe en una tabla."""
    query = f"""
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{column_name}'
    """
    return connection.execute(text(query)).scalar() == 1

def table_exists(connection, table_name):
    """Verifica si una tabla existe."""
    query = f"""
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
    """
    return connection.execute(text(query)).scalar() == 1

def migrate():
    print("Iniciando migración de la base de datos...")
    
    with engine.connect() as connection:
        # Paso 1: Crear la tabla 'media' si no existe
        if not table_exists(connection, 'media'):
            print("1. Creando la tabla 'media'...")
            connection.execute(text("""
            CREATE TABLE media (
                id INTEGER NOT NULL AUTO_INCREMENT,
                name VARCHAR(100),
                PRIMARY KEY (id),
                UNIQUE (name)
            );
            """))
            print("   ✅ Tabla 'media' creada.")
        else:
            print("1. La tabla 'media' ya existe, saltando.")

        # Paso 2: Añadir la columna 'classification' a 'noticias' si no existe
        if not column_exists(connection, 'noticias', 'classification'):
            print("2. Añadiendo columna 'classification' a 'noticias'...")
            connection.execute(text("ALTER TABLE noticias ADD COLUMN classification VARCHAR(50) NULL;"))
            print("   ✅ Columna 'classification' añadida.")
        else:
            print("2. La columna 'classification' ya existe, saltando.")
            
        # Paso 3: Migrar 'media_id' de String a Integer con Foreign Key
        # Verificamos si la columna es de tipo string (VARCHAR) antes de intentar migrarla
        media_id_type_query = """
        SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_schema = DATABASE() AND table_name = 'noticias' AND column_name = 'media_id'
        """
        media_id_type = connection.execute(text(media_id_type_query)).scalar()

        if media_id_type == 'varchar':
            print("3. Migrando la columna 'media_id'...")
            
            # 3a: Poblar 'media' con valores únicos de 'noticias.media_id'
            print("   - Poblando 'media' con datos únicos...")
            connection.execute(text("""
            INSERT IGNORE INTO media (name) SELECT DISTINCT media_id FROM noticias WHERE media_id IS NOT NULL;
            """))

            # 3b: Añadir columna temporal
            print("   - Añadiendo columna temporal 'media_id_temp'...")
            connection.execute(text("ALTER TABLE noticias ADD COLUMN media_id_temp INTEGER;"))
            
            # 3c: Actualizar la columna temporal con los IDs de la tabla 'media'
            print("   - Actualizando valores en 'media_id_temp'...")
            connection.execute(text("""
            UPDATE noticias n JOIN media m ON n.media_id = m.name SET n.media_id_temp = m.id;
            """))

            # 3d: Eliminar la columna original y renombrar la temporal
            print("   - Reemplazando la columna antigua 'media_id'...")
            connection.execute(text("ALTER TABLE noticias DROP COLUMN media_id;"))
            connection.execute(text("ALTER TABLE noticias CHANGE media_id_temp media_id INTEGER;"))
            
            # 3e: Añadir la restricción de clave foránea
            print("   - Añadiendo restricción de clave foránea...")
            connection.execute(text("""
            ALTER TABLE noticias ADD CONSTRAINT fk_media_id FOREIGN KEY (media_id) REFERENCES media(id);
            """))
            print("   ✅ Columna 'media_id' migrada.")
        else:
            print("3. La columna 'media_id' no es de tipo VARCHAR, se asume que ya está migrada. Saltando.")

        # Paso 4: Poblar 'classification' desde 'es_accidente_transito' y limpiar columnas
        if column_exists(connection, 'noticias', 'es_accidente_transito'):
            print("4. Poblando la columna 'classification' a partir de datos existentes...")
            
            # Poblar la nueva columna
            connection.execute(text("UPDATE noticias SET classification = 'ACCIDENTE' WHERE es_accidente_transito = 1;"))
            connection.execute(text("UPDATE noticias SET classification = 'NO_ACCIDENTE' WHERE es_accidente_transito = 0;"))
            connection.execute(text("UPDATE noticias SET classification = 'SIN_CLASIFICAR' WHERE classification IS NULL;"))
            print("   ✅ Columna 'classification' poblada.")

            # Eliminar columnas antiguas
            print("   - Eliminando columnas de clasificación antiguas...")
            for col_name in ['es_accidente_transito', 'es_accidente_simple', 'es_accidente_stem', 'es_accidente_lemma', 'es_accidente_ml']:
                if column_exists(connection, 'noticias', col_name):
                    connection.execute(text(f"ALTER TABLE noticias DROP COLUMN {col_name};"))
                    print(f"     - Columna '{col_name}' eliminada.")
            print("   ✅ Columnas antiguas eliminadas.")
        else:
            print("4. Las columnas de clasificación antiguas no existen, se asume que ya está migrado. Saltando.")
        
        # Commit de la transacción
        connection.commit()

    print("✅ Migración completada.")

if __name__ == "__main__":
    migrate() 