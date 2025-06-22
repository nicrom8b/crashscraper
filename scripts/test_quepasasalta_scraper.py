#!/usr/bin/env python3
"""
Script de prueba para el scraper de Que Pasa Salta.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.quepasasalta import QuePasaSaltaScraper
from app.scrapers import FECHA_LIMITE_TEST
from app.db import get_db, Noticia
import datetime

def test_quepasasalta_scraper():
    """Prueba el scraper de Que Pasa Salta."""
    print("🧪 Iniciando prueba del scraper Que Pasa Salta...")
    
    # Crear instancia del scraper con fecha límite de prueba
    scraper = QuePasaSaltaScraper(fecha_limite=FECHA_LIMITE_TEST)
    
    print(f"📅 Fecha límite configurada: {FECHA_LIMITE_TEST}")
    print(f"🌐 URL base: {scraper.BASE_URL}")
    print(f"📰 URL de policiales: {scraper.POLICIALES_URL}")
    print(f"🔄 URL AJAX: {scraper.AJAX_URL}")
    print(f"🆔 ID de categoría: {scraper.CATEGORY_ID}")
    
    # Obtener sesión de base de datos
    db = get_db()
    
    try:
        # Ejecutar el scraper
        print("\n🚀 Ejecutando scraper...")
        noticias_guardadas = scraper.scrape(db)
        
        print(f"\n✅ Scraping completado. Noticias guardadas: {noticias_guardadas}")
        
        # Mostrar las noticias guardadas
        if noticias_guardadas > 0:
            print("\n📋 Noticias extraídas:")
            noticias = db.query(Noticia).filter(Noticia.media_id == 'quepasasalta').order_by(Noticia.fecha.desc()).limit(5).all()
            
            for i, noticia in enumerate(noticias, 1):
                print(f"\n{i}. {noticia.titulo}")
                print(f"   📅 Fecha: {noticia.fecha}")
                print(f"   🔗 URL: {noticia.url}")
                print(f"   📝 Contenido: {noticia.contenido[:100]}...")
        
    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_quepasasalta_scraper() 