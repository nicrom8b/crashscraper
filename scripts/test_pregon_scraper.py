#!/usr/bin/env python3
"""
Script para probar el scraper de Pregón con el método "Ver Más"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.pregon import PregonScraper
from app.db import get_db, Noticia
from datetime import datetime, timedelta
from app.scrapers import FECHA_LIMITE_TEST

def test_pregon_vermas():
    """Prueba el scraper de Pregón con el método 'Ver Más'"""
    
    print("🧪 Probando scraper de Pregón con método 'Ver Más'...")
    
    # Configurar fecha límite usando la constante
    fecha_limite = FECHA_LIMITE_TEST
    print(f"📅 Fecha límite: {fecha_limite}")
    
    # Inicializar base de datos
    db = get_db()
    
    try:
        # Crear scraper
        scraper = PregonScraper(fecha_limite=fecha_limite)
        
        # Ejecutar scraping
        noticias_guardadas = scraper.scrape(db)
        
        print(f"\n📊 Resultados:")
        print(f"   ✅ Noticias guardadas: {noticias_guardadas}")
        
        # Verificar las noticias guardadas
        noticias = db.query(Noticia).filter(Noticia.media_id == 'pregon').order_by(Noticia.fecha.desc()).all()
        
        print(f"   📄 Total de noticias en BD: {len(noticias)}")
        
        if noticias:
            print(f"\n📅 Fechas de las noticias:")
            fechas_unicas = set()
            for noticia in noticias:
                if noticia.fecha:
                    if hasattr(noticia.fecha, 'date'):
                        fechas_unicas.add(noticia.fecha.date())
                    else:
                        fechas_unicas.add(noticia.fecha)
            
            fechas_ordenadas = sorted(fechas_unicas, reverse=True)
            for fecha in fechas_ordenadas[:10]:  # Mostrar las 10 fechas más recientes
                count = len([n for n in noticias if n.fecha and (n.fecha.date() if hasattr(n.fecha, 'date') else n.fecha) == fecha])
                print(f"   📅 {fecha}: {count} noticias")
            
            # Mostrar algunas noticias de ejemplo
            print(f"\n📰 Ejemplos de noticias:")
            for i, noticia in enumerate(noticias[:5]):
                fecha_str = noticia.fecha.strftime("%Y-%m-%d") if noticia.fecha else "Sin fecha"
                print(f"   {i+1}. [{fecha_str}] {noticia.titulo[:60]}...")
        
        # Verificar que se respetó la fecha límite
        if fecha_limite:
            noticias_antiguas = db.query(Noticia).filter(
                Noticia.media_id == 'pregon',
                Noticia.fecha < fecha_limite
            ).count()
            
            if noticias_antiguas == 0:
                print(f"✅ Se respetó correctamente la fecha límite")
            else:
                print(f"⚠️ Se encontraron {noticias_antiguas} noticias anteriores a la fecha límite")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_pregon_vermas() 