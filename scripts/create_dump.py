#!/usr/bin/env python3
"""
Script para crear un dump de la base de datos
"""

import subprocess
import datetime
import os

def create_database_dump():
    """Crea un dump de la base de datos MariaDB."""
    
    # Configuración de la base de datos
    DB_HOST = "localhost"
    DB_PORT = "3306"
    DB_USER = "root"
    DB_PASSWORD = "example"
    DB_NAME = "accidentes_craper"
    
    # Crear nombre del archivo con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_filename = f"dump_accidentes_craper_{timestamp}.sql"
    dump_path = os.path.join("dumps", dump_filename)
    
    # Crear directorio dumps si no existe
    os.makedirs("dumps", exist_ok=True)
    
    # Comando mysqldump
    cmd = [
        "mysqldump",
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--user={DB_USER}",
        f"--password={DB_PASSWORD}",
        "--single-transaction",
        "--routines",
        "--triggers",
        "--add-drop-database",
        "--create-options",
        DB_NAME
    ]
    
    print(f"🗄️  Creando dump de la base de datos...")
    print(f"📁 Archivo: {dump_path}")
    print(f"🔗 Host: {DB_HOST}:{DB_PORT}")
    print(f"📊 Base de datos: {DB_NAME}")
    
    try:
        # Ejecutar mysqldump
        with open(dump_path, 'w') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )
        
        if result.returncode == 0:
            print(f"✅ Dump creado exitosamente: {dump_path}")
            
            # Mostrar información del archivo
            file_size = os.path.getsize(dump_path)
            print(f"📏 Tamaño del archivo: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            return dump_path
        else:
            print(f"❌ Error al crear el dump:")
            print(result.stderr)
            return None
            
    except FileNotFoundError:
        print("❌ Error: mysqldump no encontrado. Asegúrate de tener MySQL/MariaDB instalado.")
        print("💡 En macOS puedes instalarlo con: brew install mysql")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

if __name__ == "__main__":
    create_database_dump() 