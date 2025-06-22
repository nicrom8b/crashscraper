#!/usr/bin/env python3
"""
Script para probar el InformateSaltaScraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.scrapers.informate_salta import InformateSaltaScraper
from app.scrapers import FECHA_LIMITE_TEST
import datetime

def test_informate_salta_scraper():
    """Prueba el scraper de Informate Salta"""
    
    print("🧪 Testing InformateSaltaScraper...")
    
    # Crear instancia del scraper
    scraper = InformateSaltaScraper(fecha_limite=FECHA_LIMITE_TEST)
    
    # Obtener conexión a la base de datos
    db = SessionLocal()
    
    try:
        # Ejecutar el scraper
        noticias_guardadas = scraper.scrape(db)
        
        print(f"✅ Scraping completado. Se guardaron {noticias_guardadas} noticias.")
        
        # Verificar cuántas noticias hay en la base de datos para este medio
        from app.db import Noticia
        total_noticias = db.query(Noticia).filter(Noticia.media_id == 'informate_salta').count()
        print(f"📊 Total de noticias de Informate Salta en la base de datos: {total_noticias}")
        
        # Mostrar las últimas noticias guardadas
        ultimas_noticias = db.query(Noticia).filter(
            Noticia.media_id == 'informate_salta'
        ).order_by(Noticia.fecha.desc()).limit(5).all()
        
        if ultimas_noticias:
            print("\n📰 Últimas noticias guardadas:")
            for i, noticia in enumerate(ultimas_noticias, 1):
                print(f"{i}. {noticia.titulo[:60]}...")
                print(f"   Fecha: {noticia.fecha}")
                print(f"   URL: {noticia.url}")
                print()
        
    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_informate_salta_scraper() 