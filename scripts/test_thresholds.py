#!/usr/bin/env python3
"""
Script para probar diferentes thresholds en los clasificadores.
"""

import sys
import os

# Agregar el directorio app al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.scraper_runner import run_classifiers_with_custom_thresholds
from app.classifiers import DEFAULT_THRESHOLDS

def test_different_thresholds():
    """Prueba diferentes configuraciones de thresholds"""
    
    print("=== PRUEBAS DE THRESHOLDS ===\n")
    
    # 1. Thresholds por defecto
    print("1. Ejecutando con thresholds por defecto:")
    print(f"   {DEFAULT_THRESHOLDS}")
    run_classifiers_with_custom_thresholds(DEFAULT_THRESHOLDS)
    print()
    
    # 2. Thresholds más estrictos (requiere más términos)
    strict_thresholds = {
        'simple': 2,        # Requiere al menos 2 términos
        'stemmer': 2,       # Requiere al menos 2 términos
        'lemmatizer': 2,    # Requiere al menos 2 términos
        'ml_weighted': 3    # Requiere score mínimo de 3
    }
    print("2. Ejecutando con thresholds estrictos:")
    print(f"   {strict_thresholds}")
    run_classifiers_with_custom_thresholds(strict_thresholds)
    print()
    
    # 3. Thresholds más permisivos (requiere menos términos)
    lenient_thresholds = {
        'simple': 1,        # Requiere al menos 1 término
        'stemmer': 1,       # Requiere al menos 1 término
        'lemmatizer': 1,    # Requiere al menos 1 término
        'ml_weighted': 1    # Requiere score mínimo de 1
    }
    print("3. Ejecutando con thresholds permisivos:")
    print(f"   {lenient_thresholds}")
    run_classifiers_with_custom_thresholds(lenient_thresholds)
    print()

if __name__ == "__main__":
    test_different_thresholds() 