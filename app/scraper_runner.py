import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, Noticia
from app.scrapers import SCRAPERS, FECHA_LIMITE_GLOBAL
from app.classifier import clasificar_noticia_completa
from app.classifiers import DEFAULT_THRESHOLDS
from sqlalchemy import or_
import datetime
import time
import argparse

def run_classifiers(custom_thresholds=None, force_reclassify=False):
    """Ejecuta todos los clasificadores en las noticias sin clasificar"""
    print("🔄 Iniciando proceso de clasificación...")
    start_time = time.time()
    
    db = SessionLocal()
    
    try:
        # Usar thresholds personalizados o los por defecto
        thresholds = custom_thresholds or DEFAULT_THRESHOLDS
        print(f"📊 Thresholds configurados: {thresholds}")
        
        # Clasificar noticias sin clasificar o todas si force_reclassify=True
        if force_reclassify:
            print("🔍 Forzando re-clasificación de TODAS las noticias...")
            noticias_a_procesar = db.query(Noticia).all()
        else:
            print("🔍 Buscando noticias sin clasificar...")
            noticias_a_procesar = db.query(Noticia).filter(
                or_(
                    Noticia.classification.is_(None),
                    Noticia.classification == 'SIN_CLASIFICAR'
                )
            ).all()
        
        print(f"📰 Encontradas {len(noticias_a_procesar)} noticias para procesar")
        
        if len(noticias_a_procesar) == 0:
            if force_reclassify:
                print("✅ No hay noticias en la base de datos")
            else:
                print("✅ No hay noticias pendientes de clasificación")
            return 0
        
        # Contadores
        stats = {'ACCIDENTE': 0, 'NO_ACCIDENTE': 0}
        
        print("🚀 Iniciando clasificación de noticias...")
        for i, noticia in enumerate(noticias_a_procesar, 1):
            print(f"  📝 Procesando noticia {i}/{len(noticias_a_procesar)}: {noticia.titulo[:50]}...")
            
            # Clasificar y obtener el resultado final y los votos individuales
            resultado_final, votos_individuales = clasificar_noticia_completa(
                noticia.titulo, 
                noticia.contenido, 
                thresholds=thresholds
            )
            
            # Guardar el resultado final
            noticia.classification = resultado_final
            noticia.es_accidente_transito = (resultado_final == 'ACCIDENTE')
            
            # Guardar los votos individuales
            noticia.es_accidente_simple = votos_individuales.get('simple')
            noticia.es_accidente_stem = votos_individuales.get('stemmer')
            noticia.es_accidente_lemma = votos_individuales.get('lemmatizer')
            noticia.es_accidente_ml = votos_individuales.get('ml_weighted')

            stats[resultado_final] += 1
                
            print(f"    -> Resultado: {resultado_final}")
            
            # Guardar cada 10 noticias para evitar pérdida de datos
            if i % 10 == 0:
                db.commit()
                print(f"💾 Guardado progreso ({i}/{len(noticias_a_procesar)})")

        # Guardar cambios finales
        db.commit()
        end_time = time.time()
        
        print(f"\n🎉 Clasificación completada en {end_time - start_time:.2f} segundos")
        print("📊 Resumen de clasificación:")
        print(f"  - Accidentes: {stats['ACCIDENTE']}")
        print(f"  - No Accidentes: {stats['NO_ACCIDENTE']}")
        print(f"💾 Total noticias clasificadas: {len(noticias_a_procesar)}")
        
        return len(noticias_a_procesar)
    finally:
        db.close()

def run_classifiers_with_custom_thresholds(thresholds):
    """Ejecuta clasificadores con thresholds personalizados"""
    print(f"Ejecutando clasificadores con thresholds personalizados: {thresholds}")
    return run_classifiers(custom_thresholds=thresholds)

def force_reclassify_all():
    """Fuerza la re-clasificación de todas las noticias"""
    print("🔄 Forzando re-clasificación de todas las noticias...")
    return run_classifiers(force_reclassify=True)

def run_all_scrapers(fecha_limite_arg=None):
    db = SessionLocal()
    total_noticias_scrapeadas = 0
    try:
        # Decidir qué fecha límite usar
        fecha_a_usar = None
        if fecha_limite_arg:
            try:
                fecha_a_usar = datetime.datetime.strptime(fecha_limite_arg, '%Y-%m-%d').date()
                print(f"🗓️  Usando fecha límite de la interfaz: {fecha_a_usar.strftime('%Y-%m-%d')}")
            except ValueError:
                print(f"⚠️  Fecha inválida '{fecha_limite_arg}'. Usando la fecha global por defecto.")
                fecha_a_usar = FECHA_LIMITE_GLOBAL
        else:
            fecha_a_usar = FECHA_LIMITE_GLOBAL
            print(f"🗓️  Usando fecha límite global por defecto: {fecha_a_usar.strftime('%Y-%m-%d')}")

        # Instanciamos los scrapers pasándoles la fecha límite decidida
        scrapers_con_limite = [ScraperClass(fecha_limite=fecha_a_usar) for ScraperClass in SCRAPERS]

        for scraper in scrapers_con_limite:
            print(f"▶️  Ejecutando scraper: {scraper.__class__.__name__}")
            try:
                guardadas = scraper.scrape(db)
                print(f"  ✅ Noticias guardadas: {guardadas}")
                total_noticias_scrapeadas += guardadas
            except Exception as e:
                print(f"  ❌ Error en scraper {scraper.__class__.__name__}: {e}")
                db.rollback() # Asegurarse de revertir en caso de error en un scraper
    finally:
        db.close()
    
    # Ejecutar clasificadores después de scrapear.
    # Esta función ahora manejará su propia sesión de DB.
    print("\n🏁 Scraping finalizado. Iniciando clasificación de noticias nuevas...")
    clasificadas = run_classifiers()
    
    print(f"\n📈 Resumen final:")
    print(f"  - Total noticias nuevas scrapeadas: {total_noticias_scrapeadas}")
    print(f"  - Total noticias nuevas clasificadas: {clasificadas}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutar scrapers y clasificadores.")
    parser.add_argument("--classify-only", action="store_true", help="Ejecuta solo clasificadores en noticias sin clasificar")
    parser.add_argument("--force-reclassify", action="store_true", help="Re-clasifica TODAS las noticias")
    parser.add_argument("--fecha-limite", type=str, help="Fecha límite para los scrapers en formato YYYY-MM-DD")
    
    args = parser.parse_args()

    # Verificar argumentos de línea de comandos
    if args.classify_only:
        print("Ejecutando solo clasificadores...")
        clasificadas = run_classifiers()
        print(f"Clasificación completada. Total noticias clasificadas: {clasificadas}")
    elif args.force_reclassify:
        print("Ejecutando re-clasificación forzada...")
        clasificadas = force_reclassify_all()
        print(f"Re-clasificación completada. Total noticias procesadas: {clasificadas}")
    else:
        # Ejecutar scraping completo, pasando la fecha si se proveyó
        run_all_scrapers(fecha_limite_arg=args.fecha_limite)
        print("Scraping y guardado completados.") 