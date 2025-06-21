#!/usr/bin/env python3
"""
Script para ejecutar solo los clasificadores en las noticias existentes.
"""

import sys
import os

# Agregar el directorio app al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.scraper_runner import run_classifiers, force_reclassify_all

if __name__ == "__main__":
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔄 Ejecutando re-clasificación forzada de todas las noticias...")
        clasificadas = force_reclassify_all()
        print(f"Re-clasificación completada. Total noticias procesadas: {clasificadas}")
    else:
        print("Ejecutando solo clasificadores...")
        clasificadas = run_classifiers()
        print(f"Clasificación completada. Total noticias clasificadas: {clasificadas}")
        print("\n💡 Para re-clasificar TODAS las noticias, usa: python scripts/run_classifiers.py --force") 