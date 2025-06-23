#!/usr/bin/env python3
"""
Script de prueba para la API de Crashscraper
"""

import requests
import json
import sys
import time

def test_api():
    """Prueba los endpoints de la API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Probando API de Crashscraper...")
    print(f"🌐 URL base: {base_url}")
    
    # Test 1: Endpoint raíz
    print("\n1️⃣ Probando endpoint raíz...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint raíz OK: {data['message']}")
            print(f"📋 Endpoints disponibles: {list(data['endpoints'].keys())}")
        else:
            print(f"❌ Error en endpoint raíz: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando a la API: {e}")
        return
    
    # Test 2: Estado de Ollama
    print("\n2️⃣ Verificando estado de Ollama...")
    try:
        response = requests.get(f"{base_url}/ollama/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama disponible: {data['ollama_disponible']}")
            if data['ollama_disponible']:
                print(f"📋 Modelos disponibles: {data['modelos_disponibles']}")
            else:
                print(f"⚠️  Ollama no disponible: {data.get('error', 'Sin detalles')}")
        else:
            print(f"❌ Error verificando Ollama: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Estadísticas
    print("\n3️⃣ Obteniendo estadísticas...")
    try:
        response = requests.get(f"{base_url}/estadisticas")
        if response.status_code == 200:
            data = response.json()
            stats = data['estadisticas']
            print(f"✅ Estadísticas obtenidas:")
            print(f"   📊 Total noticias: {stats['total_noticias']}")
            print(f"   🚗 Accidentes de tránsito: {stats['accidentes_transito']}")
            print(f"   ❌ No accidentes: {stats['no_accidentes_transito']}")
            print(f"   ❓ Sin clasificar: {stats['sin_clasificar']}")
            print(f"   📰 Por medio: {stats['por_medio']}")
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Búsqueda simple
    print("\n4️⃣ Probando búsqueda simple...")
    try:
        response = requests.get(f"{base_url}/buscar?q=accidente&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Búsqueda exitosa:")
            print(f"   🔍 Término: {data['termino_busqueda']}")
            print(f"   📊 Resultados: {data['total_resultados']}")
            if data['noticias']:
                print(f"   📰 Primera noticia: {data['noticias'][0]['titulo'][:50]}...")
        else:
            print(f"❌ Error en búsqueda: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Consulta con LLM (solo si hay datos)
    print("\n5️⃣ Probando consulta con LLM...")
    try:
        # Primero verificar si hay datos
        stats_response = requests.get(f"{base_url}/estadisticas")
        if stats_response.status_code == 200:
            stats = stats_response.json()['estadisticas']
            if stats['total_noticias'] > 0:
                response = requests.get(f"{base_url}/consultar?pregunta=¿Cuántos accidentes de tránsito hay?")
                if response.status_code == 200:
                    data = response.json()
                    if 'error' in data:
                        print(f"⚠️  Error en consulta LLM: {data['error']}")
                    else:
                        print(f"✅ Consulta LLM exitosa:")
                        print(f"   ❓ Pregunta: {data['pregunta']}")
                        print(f"   🤖 Respuesta: {data['respuesta'][:100]}...")
                        print(f"   📰 Noticias encontradas: {data['total_noticias_encontradas']}")
                else:
                    print(f"❌ Error en consulta LLM: {response.status_code}")
            else:
                print("⚠️  No hay noticias en la base de datos para probar la consulta LLM")
        else:
            print(f"❌ Error obteniendo estadísticas para verificar datos: {stats_response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Listar noticias
    print("\n6️⃣ Probando listado de noticias...")
    try:
        response = requests.get(f"{base_url}/noticias?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listado exitoso:")
            print(f"   📊 Total: {data['total']}")
            print(f"   📰 Mostrando: {len(data['noticias'])} noticias")
            if data['noticias']:
                print(f"   📋 Primera: {data['noticias'][0]['titulo'][:50]}...")
        else:
            print(f"❌ Error en listado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_api() 