#!/usr/bin/env python3
"""
Script para probar el scraper de El Submarino Jujuy.
"""

import sys
import os
from datetime import datetime, timedelta

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.elsubmarinojujuy import ElSubmarinoJujuyScraper
from app.scrapers import FECHA_LIMITE_TEST
from app.db import get_db, Noticia

def test_elsubmarino_scraper():
    """Prueba el scraper de El Submarino Jujuy."""
    
    print("🧪  Probando scraper de El Submarino Jujuy...")
    
    # Usar la fecha límite de testeo estándar
    fecha_limite = FECHA_LIMITE_TEST
    print(f"📅 Fecha límite establecida: {fecha_limite}")
    
    db = get_db()
    
    try:
        # Contar noticias antes del scraping
        count_before = db.query(Noticia).filter(Noticia.media_id == 'elsubmarinojujuy').count()
        print(f"📄 Noticias de 'elsubmarinojujuy' en la BD antes: {count_before}")

        # Crear y ejecutar el scraper
        scraper = ElSubmarinoJujuyScraper(fecha_limite=fecha_limite)
        noticias_guardadas = scraper.scrape(db)
        
        print("\n📊 Resultados del Scraping:")
        print(f"   ✅ Noticias nuevas guardadas: {noticias_guardadas}")
        
        # Contar noticias después del scraping
        count_after = db.query(Noticia).filter(Noticia.media_id == 'elsubmarinojujuy').count()
        print(f"   📄 Total de noticias de 'elsubmarinojujuy' en la BD: {count_after}")
        assert count_after >= count_before

        # Verificar que se respetó la fecha límite
        if fecha_limite:
            noticias_antiguas = db.query(Noticia).filter(
                Noticia.media_id == 'elsubmarinojujuy',
                Noticia.fecha < fecha_limite
            ).count()
            
            if noticias_antiguas == 0:
                print(f"   👍 Se respetó correctamente la fecha límite. No hay noticias anteriores a {fecha_limite}.")
            else:
                print(f"   ⚠️ ¡Alerta! Se encontraron {noticias_antiguas} noticias más antiguas que la fecha límite.")

        # Imprimir algunas noticias de ejemplo
        print("\n📰 Ejemplos de noticias scrapeadas:")
        ultimas_noticias = db.query(Noticia).filter(Noticia.media_id == 'elsubmarinojujuy').order_by(Noticia.fecha.desc()).limit(5).all()
        for i, noticia in enumerate(ultimas_noticias):
            fecha_str = noticia.fecha.strftime('%Y-%m-%d') if noticia.fecha else "Sin Fecha"
            print(f"   {i+1}. [{fecha_str}] - {noticia.titulo[:70]}...")

    except Exception as e:
        print(f"❌ Error catastrófico durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print("\n🏁 Prueba finalizada.")

if __name__ == "__main__":
    test_elsubmarino_scraper() 