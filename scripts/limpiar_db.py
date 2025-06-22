#!/usr/bin/env python3
"""
Script para limpiar la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, Noticia

if __name__ == "__main__":
    db = SessionLocal()
    try:
        deleted = db.query(Noticia).delete()
        db.commit()
        print(f"Se eliminaron {deleted} registros de la tabla 'noticias'.")
    except Exception as e:
        db.rollback()
        print(f"Error al limpiar la base de datos: {e}")
    finally:
        db.close() 