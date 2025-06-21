from app.db import SessionLocal, Noticia
from app.scrapers import SCRAPERS
from app.classifiers.simple import es_accidente_simple
from app.classifiers.stemmer import es_accidente_stemmer
from app.classifiers.lemmatizer import es_accidente_lemmatizer
from app.classifiers.ml_weighted import es_accidente_ml_weighted
from app.classifiers import DEFAULT_THRESHOLDS
import datetime
import time

def run_classifiers(custom_thresholds=None, force_reclassify=False):
    """Ejecuta todos los clasificadores en las noticias sin clasificar"""
    print("🔄 Iniciando proceso de clasificación...")
    start_time = time.time()
    
    db = SessionLocal()
    
    # Usar thresholds personalizados o los por defecto
    thresholds = custom_thresholds or DEFAULT_THRESHOLDS
    print(f"📊 Thresholds configurados: {thresholds}")
    
    # Clasificar noticias sin clasificar o todas si force_reclassify=True
    if force_reclassify:
        print("🔍 Forzando re-clasificación de TODAS las noticias...")
        sin_clasificar = db.query(Noticia).all()
    else:
        print("🔍 Buscando noticias sin clasificar...")
        sin_clasificar = db.query(Noticia).filter(
            (Noticia.es_accidente_simple == None) |
            (Noticia.es_accidente_stem == None) |
            (Noticia.es_accidente_lemma == None) |
            (Noticia.es_accidente_ml == None)
        ).all()
    
    print(f"📰 Encontradas {len(sin_clasificar)} noticias para procesar")
    
    if len(sin_clasificar) == 0:
        if force_reclassify:
            print("✅ No hay noticias en la base de datos")
        else:
            print("✅ No hay noticias pendientes de clasificación")
        db.close()
        return 0
    
    # Contadores para cada clasificador
    resultados = {
        'simple': {'accidentes': 0, 'no_accidentes': 0},
        'stemmer': {'accidentes': 0, 'no_accidentes': 0},
        'lemmatizer': {'accidentes': 0, 'no_accidentes': 0},
        'ml_weighted': {'accidentes': 0, 'no_accidentes': 0}
    }
    
    print("🚀 Iniciando clasificación de noticias...")
    for i, noticia in enumerate(sin_clasificar, 1):
        print(f"\n📝 Procesando noticia {i}/{len(sin_clasificar)}: {noticia.titulo[:50]}...")
        
        # Clasificador Simple
        print("  🔸 Ejecutando clasificador Simple...")
        resultado_simple = es_accidente_simple(
            noticia.titulo, 
            noticia.contenido, 
            threshold=thresholds['simple']
        )
        noticia.es_accidente_simple = resultado_simple
        if resultado_simple:
            resultados['simple']['accidentes'] += 1
        else:
            resultados['simple']['no_accidentes'] += 1
        print(f"    Resultado: {'✅ ACCIDENTE' if resultado_simple else '❌ NO ACCIDENTE'}")
        
        # Clasificador Stemmer
        print("  🔸 Ejecutando clasificador Stemmer...")
        resultado_stem = es_accidente_stemmer(
            noticia.titulo, 
            noticia.contenido, 
            threshold=thresholds['stemmer']
        )
        noticia.es_accidente_stem = resultado_stem
        if resultado_stem:
            resultados['stemmer']['accidentes'] += 1
        else:
            resultados['stemmer']['no_accidentes'] += 1
        print(f"    Resultado: {'✅ ACCIDENTE' if resultado_stem else '❌ NO ACCIDENTE'}")
        
        # Clasificador Lemmatizer
        print("  🔸 Ejecutando clasificador Lemmatizer...")
        resultado_lemma = es_accidente_lemmatizer(
            noticia.titulo, 
            noticia.contenido, 
            threshold=thresholds['lemmatizer']
        )
        noticia.es_accidente_lemma = resultado_lemma
        if resultado_lemma:
            resultados['lemmatizer']['accidentes'] += 1
        else:
            resultados['lemmatizer']['no_accidentes'] += 1
        print(f"    Resultado: {'✅ ACCIDENTE' if resultado_lemma else '❌ NO ACCIDENTE'}")
        
        # Clasificador ML Weighted
        print("  🔸 Ejecutando clasificador ML Weighted...")
        resultado_ml = es_accidente_ml_weighted(
            noticia.titulo, 
            noticia.contenido, 
            threshold=thresholds['ml_weighted']
        )
        noticia.es_accidente_ml = resultado_ml
        if resultado_ml:
            resultados['ml_weighted']['accidentes'] += 1
        else:
            resultados['ml_weighted']['no_accidentes'] += 1
        print(f"    Resultado: {'✅ ACCIDENTE' if resultado_ml else '❌ NO ACCIDENTE'}")
        
        # Guardar cada 10 noticias para evitar pérdida de datos
        if i % 10 == 0:
            db.commit()
            print(f"💾 Guardado progreso ({i}/{len(sin_clasificar)})")

    # Guardar cambios finales
    db.commit()
    end_time = time.time()
    
    print(f"\n🎉 Clasificación completada en {end_time - start_time:.2f} segundos")
    print(f"📊 Resumen de resultados:")
    for clasificador, stats in resultados.items():
        total = stats['accidentes'] + stats['no_accidentes']
        porcentaje = (stats['accidentes'] / total * 100) if total > 0 else 0
        print(f"  {clasificador.upper()}: {stats['accidentes']} accidentes, {stats['no_accidentes']} no accidentes ({porcentaje:.1f}% accidentes)")
    
    print(f"💾 Total noticias clasificadas: {len(sin_clasificar)}")
    db.close()
    
    return len(sin_clasificar)

def run_classifiers_with_custom_thresholds(thresholds):
    """Ejecuta clasificadores con thresholds personalizados"""
    print(f"Ejecutando clasificadores con thresholds personalizados: {thresholds}")
    return run_classifiers(custom_thresholds=thresholds)

def force_reclassify_all():
    """Fuerza la re-clasificación de todas las noticias"""
    print("🔄 Forzando re-clasificación de todas las noticias...")
    return run_classifiers(force_reclassify=True)

def run_all_scrapers():
    db = SessionLocal()
    total_noticias = 0
    for scraper in SCRAPERS:
        print(f"Ejecutando scraper: {scraper.__class__.__name__}")
        guardadas = scraper.scrape(db)
        print(f"  Noticias guardadas: {guardadas}")
        total_noticias += guardadas

    db.close()
    
    # Ejecutar clasificadores por separado
    clasificadas = run_classifiers()
    
    print(f"Total noticias scrapeadas: {total_noticias}")
    print(f"Total noticias clasificadas: {clasificadas}")

if __name__ == "__main__":
    import sys
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--classify-only":
            print("Ejecutando solo clasificadores...")
            clasificadas = run_classifiers()
            print(f"Clasificación completada. Total noticias clasificadas: {clasificadas}")
        elif sys.argv[1] == "--force-reclassify":
            print("Ejecutando re-clasificación forzada...")
            clasificadas = force_reclassify_all()
            print(f"Re-clasificación completada. Total noticias procesadas: {clasificadas}")
        else:
            print("Uso: python scraper_runner.py [--classify-only|--force-reclassify]")
            print("  --classify-only: Ejecuta solo clasificadores en noticias sin clasificar")
            print("  --force-reclassify: Re-clasifica TODAS las noticias")
    else:
        # Ejecutar scraping completo
        run_all_scrapers()
        print("Scraping y guardado completados.") 