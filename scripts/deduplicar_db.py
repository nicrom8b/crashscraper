#!/usr/bin/env python3
"""
Script para eliminar noticias duplicadas de la base de datos, conservando la primera entrada.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, Noticia
from sqlalchemy import func

def deduplicar_noticias():
    """
    Busca y elimina noticias duplicadas basadas en la URL, conservando la primera registrada (menor ID).
    """
    db = SessionLocal()
    print("🔍 Buscando noticias duplicadas...")

    try:
        # 1. Encontrar URLs duplicadas y contar cuántas hay de cada una
        urls_duplicadas = db.query(
            Noticia.url, 
            func.count(Noticia.id).label('cantidad')
        ).group_by(Noticia.url).having(func.count(Noticia.id) > 1).all()

        if not urls_duplicadas:
            print("✅ No se encontraron noticias duplicadas.")
            return

        print(f" 발견된 {len(urls_duplicadas)}개의 중복된 URL을 처리합니다...")
        total_eliminadas = 0

        for url, cantidad in urls_duplicadas:
            # 2. Para cada URL duplicada, encontrar todos los IDs asociados
            ids = db.query(Noticia.id).filter(Noticia.url == url).order_by(Noticia.id.asc()).all()
            
            # 3. Conservar el primer ID y marcar el resto para eliminación
            ids_a_eliminar = [item[0] for item in ids[1:]]
            
            if ids_a_eliminar:
                db.query(Noticia).filter(Noticia.id.in_(ids_a_eliminar)).delete(synchronize_session=False)
                db.commit()
                print(f"🗑️ Eliminadas {len(ids_a_eliminar)} copias de: {url}")
                total_eliminadas += len(ids_a_eliminar)
        
        print(f"\n🎉 Proceso completado. Se eliminaron un total de {total_eliminadas} noticias duplicadas.")

    except Exception as e:
        print(f"❌ Error durante el proceso de deduplicación: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    deduplicar_noticias() 