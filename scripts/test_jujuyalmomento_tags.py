#!/usr/bin/env python3
"""
Script para probar el scraper de etiquetas de Jujuy al Momento
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.jujuyalmomento import JujuyAlMomentoTagScraper
from app.scrapers import FECHA_LIMITE_TEST
from app.db import SessionLocal

def test_jujuyalmomento_tags_scraper():
    """Prueba el scraper de etiquetas de Jujuy al Momento"""
    print("🚀 Iniciando prueba del scraper de etiquetas Jujuy al Momento...")
    print(f"📅 Usando fecha límite de test: {FECHA_LIMITE_TEST}")
    
    scraper = JujuyAlMomentoTagScraper(fecha_limite=FECHA_LIMITE_TEST)
    db = SessionLocal()
    
    try:
        noticias_guardadas = scraper.scrape(db)
        print(f"\n🎉 Prueba completada. Se guardaron {noticias_guardadas} noticias.")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_jujuyalmomento_tags_scraper() 