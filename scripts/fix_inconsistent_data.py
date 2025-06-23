#!/usr/bin/env python3
"""
Script de un solo uso para corregir inconsistencias en la base de datos
donde la columna `classification` está poblada pero la columna
booleana `es_accidente_transito` es NULL.
"""

import sys
import os

# Añadir el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, Noticia

def fix_inconsistent_data():
    """
    Busca noticias donde `classification` está definido pero `es_accidente_transito`
    es NULL y actualiza este último para que coincida.
    """
    db = SessionLocal()
    try:
        print("🔍 Buscando noticias con datos de clasificación inconsistentes...")
        
        # Buscar todas las noticias donde `classification` tiene un valor
        # pero `es_accidente_transito` es nulo.
        inconsistent_news = db.query(Noticia).filter(
            Noticia.classification.isnot(None),
            Noticia.es_accidente_transito.is_(None)
        ).all()
        
        if not inconsistent_news:
            print("✅ ¡Perfecto! No se encontraron inconsistencias en la base de datos.")
            return

        print(f"🔧 Encontradas {len(inconsistent_news)} noticias para corregir. Actualizando ahora...")
        
        count = 0
        for noticia in inconsistent_news:
            is_accident = (noticia.classification == 'ACCIDENTE')
            noticia.es_accidente_transito = is_accident
            count += 1
        
        db.commit()
        print(f"🎉 ¡Éxito! Se han corregido {count} registros.")

    except Exception as e:
        print(f"❌ Ocurrió un error durante la corrección: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_inconsistent_data() 