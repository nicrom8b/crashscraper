#!/usr/bin/env python3
"""
Script para probar la extracción de contenido de un artículo individual de El Tribuno Salta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def test_single_article():
    """Prueba la extracción de contenido de un artículo específico"""
    
    # URL de ejemplo de un artículo de policiales
    url = "https://www.eltribuno.com/policiales/2025-6-22-14-11-0-un-incendio-boraz-destruyo-por-completo-una-casa-en-barrio-vicente-sola"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 Probando extracción de contenido de: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        print(f"📄 Tamaño del HTML: {len(response.text)} caracteres")
        
        # Buscar el título
        title_selectors = [
            'h1',
            '.title',
            '.article-title',
            '.nota__titulo',
            '.nota__titulo-item',
            'title'
        ]
        
        titulo = None
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                titulo = title_element.get_text().strip()
                print(f"📰 Título encontrado con selector '{selector}': {titulo}")
                break
        
        if not titulo:
            print("❌ No se encontró título")
        
        # Buscar el contenido
        content_selectors = [
            'article',
            '.article-content',
            '.nota-content',
            '.content',
            '.entry-content',
            'main',
            '.main-content',
            '.nota__body'
        ]
        
        print("\n🔍 Buscando contenido con diferentes selectores:")
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                paragraphs = content_element.find_all('p')
                print(f"✅ Selector '{selector}': {len(paragraphs)} párrafos encontrados")
                
                if paragraphs:
                    # Mostrar los primeros 3 párrafos
                    for i, p in enumerate(paragraphs[:3]):
                        text = p.get_text().strip()
                        if text:
                            print(f"   Párrafo {i+1}: {text[:100]}...")
                else:
                    print(f"   ⚠️ No se encontraron párrafos en este selector")
            else:
                print(f"❌ Selector '{selector}': No encontrado")
        
        # Buscar elementos con clases que contengan 'nota'
        nota_elements = soup.find_all(class_=re.compile(r'nota'))
        print(f"\n📄 Elementos con clases que contienen 'nota': {len(nota_elements)}")
        
        for i, element in enumerate(nota_elements[:5]):
            classes = ' '.join(element.get('class', []))
            print(f"   {i+1}. Clases: {classes}")
            text = element.get_text().strip()[:100]
            if text:
                print(f"      Texto: {text}...")
        
        # Buscar todos los párrafos en la página
        all_paragraphs = soup.find_all('p')
        print(f"\n📝 Total de párrafos en la página: {len(all_paragraphs)}")
        
        # Mostrar los primeros 5 párrafos con texto
        print("\n📄 Primeros 5 párrafos con contenido:")
        count = 0
        for p in all_paragraphs:
            text = p.get_text().strip()
            if text and count < 5:
                print(f"   {count+1}. {text[:150]}...")
                count += 1
        
        # Buscar elementos específicos de El Tribuno
        print("\n🔍 Elementos específicos de El Tribuno:")
        
        # Buscar elementos con clases específicas
        specific_classes = ['nota__body', 'nota__introduccion', 'nota__titulo']
        for class_name in specific_classes:
            elements = soup.find_all(class_=class_name)
            print(f"   Clase '{class_name}': {len(elements)} elementos")
            for i, element in enumerate(elements[:2]):
                text = element.get_text().strip()
                if text:
                    print(f"      {i+1}. {text[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single_article() 