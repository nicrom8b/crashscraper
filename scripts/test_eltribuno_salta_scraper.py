#!/usr/bin/env python3
"""
Test script for ElTribunoSaltaScraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.scrapers.eltribuno_salta import ElTribunoSaltaScraper
from app.scrapers import FECHA_LIMITE_TEST

def test_eltribuno_salta_scraper():
    """Test the ElTribunoSaltaScraper"""
    print("🧪 Testing ElTribunoSaltaScraper...")
    
    # Create scraper with recent date limit for testing
    scraper = ElTribunoSaltaScraper(fecha_limite=FECHA_LIMITE_TEST)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Run scraper
        noticias_guardadas = scraper.scrape(db)
        print(f"✅ Scraping completado. Se guardaron {noticias_guardadas} noticias.")
        
        # Verify some articles were saved
        from app.db import Noticia
        noticias = db.query(Noticia).filter(Noticia.media_id == 'eltribuno_salta').all()
        print(f"📊 Total de noticias de El Tribuno Salta en la base de datos: {len(noticias)}")
        
        if noticias:
            print("\n📰 Últimas noticias guardadas:")
            for i, noticia in enumerate(noticias[:5], 1):
                print(f"{i}. {noticia.titulo[:60]}...")
                print(f"   Fecha: {noticia.fecha}")
                print(f"   URL: {noticia.url}")
                print()
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_eltribuno_salta_scraper() 