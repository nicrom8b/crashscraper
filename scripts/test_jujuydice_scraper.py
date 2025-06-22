#!/usr/bin/env python3
"""
Script para probar el scraper de Jujuy Dice
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.jujuydice import JujuyDiceScraper
from app.scrapers import FECHA_LIMITE_TEST
from app.db import SessionLocal

def test_jujuydice_scraper():
    """Prueba el scraper de Jujuy Dice"""
    print("🚀 Iniciando prueba del scraper Jujuy Dice...")
    print(f"📅 Usando fecha límite de test: {FECHA_LIMITE_TEST}")
    
    scraper = JujuyDiceScraper(fecha_limite=FECHA_LIMITE_TEST)
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
    test_jujuydice_scraper() 