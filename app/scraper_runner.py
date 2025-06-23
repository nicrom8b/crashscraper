import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, Noticia
from app.scrapers import SCRAPERS
from app.classifier import clasificar_noticia_completa
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
    
    # Contadores para el voto mayoritario
    votos_mayoritarios = {'accidentes': 0, 'no_accidentes': 0}
    
    print("🚀 Iniciando clasificación de noticias...")
    for i, noticia in enumerate(sin_clasificar, 1):
        print(f"\n📝 Procesando noticia {i}/{len(sin_clasificar)}: {noticia.titulo[:50]}...")
        
        # Clasificar noticia usando la función centralizada
        resultado_clasificacion = clasificar_noticia_completa(
            noticia.titulo, 
            noticia.contenido, 
            thresholds=thresholds
        )
        
        # Extraer resultados individuales
        resultados_individuales = resultado_clasificacion['resultados_individuales']
        es_accidente_final = resultado_clasificacion['es_accidente_transito']
        
        # Guardar resultados individuales en la base de datos
        noticia.es_accidente_simple = resultados_individuales['simple']
        noticia.es_accidente_stem = resultados_individuales['stemmer']
        noticia.es_accidente_lemma = resultados_individuales['lemmatizer']
        noticia.es_accidente_ml = resultados_individuales['ml_weighted']
        noticia.es_accidente_transito = es_accidente_final
        
        # Actualizar contadores individuales
        for clasificador, resultado in resultados_individuales.items():
            if resultado:
                resultados[clasificador]['accidentes'] += 1
            else:
                resultados[clasificador]['no_accidentes'] += 1
            print(f"  🔸 {clasificador.upper()}: {'✅ ACCIDENTE' if resultado else '❌ NO ACCIDENTE'}")
        
        # Actualizar contadores del voto mayoritario
        if es_accidente_final:
            votos_mayoritarios['accidentes'] += 1
        else:
            votos_mayoritarios['no_accidentes'] += 1
            
        print(f"  🗳️  Voto mayoritario: {'✅ ACCIDENTE DE TRÁNSITO' if es_accidente_final else '❌ NO ES ACCIDENTE DE TRÁNSITO'}")
        
        # Guardar cada 10 noticias para evitar pérdida de datos
        if i % 10 == 0:
            db.commit()
            print(f"💾 Guardado progreso ({i}/{len(sin_clasificar)})")

    # Guardar cambios finales
    db.commit()
    end_time = time.time()
    
    print(f"\n🎉 Clasificación completada en {end_time - start_time:.2f} segundos")
    print(f"📊 Resumen de resultados por clasificador:")
    for clasificador, stats in resultados.items():
        total = stats['accidentes'] + stats['no_accidentes']
        porcentaje = (stats['accidentes'] / total * 100) if total > 0 else 0
        print(f"  {clasificador.upper()}: {stats['accidentes']} accidentes, {stats['no_accidentes']} no accidentes ({porcentaje:.1f}% accidentes)")
    
    print(f"\n🗳️  Resumen de voto mayoritario:")
    total_votos = votos_mayoritarios['accidentes'] + votos_mayoritarios['no_accidentes']
    porcentaje_votos = (votos_mayoritarios['accidentes'] / total_votos * 100) if total_votos > 0 else 0
    print(f"  VOTO MAYORITARIO: {votos_mayoritarios['accidentes']} accidentes de tránsito, {votos_mayoritarios['no_accidentes']} no accidentes ({porcentaje_votos:.1f}% accidentes de tránsito)")
    
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