#!/usr/bin/env python3
"""
Script para probar el scraper de TodoJujuy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.todojujuy import TodoJujuyScraper
from app.scrapers import FECHA_LIMITE_TEST
from app.db import SessionLocal

def test_todojujuy_scraper():
    """Prueba el scraper de TodoJujuy"""
    print("🚀 Iniciando prueba del scraper TodoJujuy...")
    print(f"📅 Usando fecha límite de test: {FECHA_LIMITE_TEST}")
    
    # Crea una instancia del scraper con la fecha límite de test
    scraper = TodoJujuyScraper(fecha_limite=FECHA_LIMITE_TEST)
    
    # Obtiene una sesión de base de datos
    db = SessionLocal()
    
    try:
        # Ejecuta el scraper
        noticias_guardadas = scraper.scrape(db)
        print(f"\n🎉 Prueba completada. Se guardaron {noticias_guardadas} noticias.")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_todojujuy_scraper() 