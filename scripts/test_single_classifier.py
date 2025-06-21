#!/usr/bin/env python3
"""
Script para probar un clasificador específico de forma rápida.
"""

import sys
import os

# Agregar el directorio app al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db import SessionLocal, Noticia
from app.classifiers.simple import es_accidente_simple
from app.classifiers.stemmer import es_accidente_stemmer
from app.classifiers.lemmatizer import es_accidente_lemmatizer
from app.classifiers.ml_weighted import es_accidente_ml_weighted
from app.classifiers import DEFAULT_THRESHOLDS

def test_single_classifier(classifier_name, limit=5):
    """Prueba un clasificador específico con las primeras N noticias"""
    
    classifiers = {
        'simple': es_accidente_simple,
        'stemmer': es_accidente_stemmer,
        'lemmatizer': es_accidente_lemmatizer,
        'ml_weighted': es_accidente_ml_weighted
    }
    
    if classifier_name not in classifiers:
        print(f"❌ Clasificador '{classifier_name}' no encontrado")
        print(f"Clasificadores disponibles: {list(classifiers.keys())}")
        return
    
    print(f"🧪 Probando clasificador: {classifier_name}")
    print(f"📊 Threshold: {DEFAULT_THRESHOLDS[classifier_name]}")
    
    db = SessionLocal()
    
    # Obtener algunas noticias para probar
    noticias = db.query(Noticia).limit(limit).all()
    
    if not noticias:
        print("❌ No hay noticias en la base de datos")
        db.close()
        return
    
    print(f"📰 Probando con {len(noticias)} noticias...")
    
    accidentes = 0
    no_accidentes = 0
    
    for i, noticia in enumerate(noticias, 1):
        print(f"\n📝 Noticia {i}: {noticia.titulo[:60]}...")
        
        resultado = classifiers[classifier_name](
            noticia.titulo, 
            noticia.contenido,
            threshold=DEFAULT_THRESHOLDS[classifier_name]
        )
        
        if resultado:
            accidentes += 1
            print(f"  ✅ Resultado: ACCIDENTE")
        else:
            no_accidentes += 1
            print(f"  ❌ Resultado: NO ACCIDENTE")
    
    total = len(noticias)
    porcentaje = (accidentes / total * 100) if total > 0 else 0
    
    print(f"\n📊 Resumen del clasificador {classifier_name}:")
    print(f"  Accidentes: {accidentes}")
    print(f"  No accidentes: {no_accidentes}")
    print(f"  Porcentaje de accidentes: {porcentaje:.1f}%")
    
    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_single_classifier.py <clasificador> [limite]")
        print("Clasificadores disponibles: simple, stemmer, lemmatizer, ml_weighted")
        print("Ejemplo: python test_single_classifier.py simple 3")
        sys.exit(1)
    
    classifier = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    test_single_classifier(classifier, limit) 