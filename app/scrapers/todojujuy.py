from .base import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin
import time

class TodoJujuyScraper(BaseScraper):
    BASE_URL = "https://www.todojujuy.com"
    POLICIALES_URL = "https://www.todojujuy.com/policiales"

    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.media_name = 'todojujuy'

    def scrape(self, db) -> int:
        noticias_guardadas = 0
        pagina = 0  # Comienza en 0 según el patrón de URLs
        seguir = True

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        while seguir:
            url_pagina = f"{self.POLICIALES_URL}/{pagina}" if pagina > 0 else self.POLICIALES_URL
            print(f"📄 Scraping página {pagina}: {url_pagina}")
            
            try:
                response = requests.get(url_pagina, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Busca enlaces de artículos en la página
                # Los artículos suelen estar en enlaces <a> con URLs que contienen el patrón de ID
                article_links = soup.find_all('a', href=re.compile(r'n\d+$'))
                
                if not article_links:
                    print(f"🤷 No se encontraron más artículos en la página {pagina}")
                    break

                found_articles = False
                
                for link in article_links:
                    try:
                        url = urljoin(self.BASE_URL, link['href'])
                        
                        # Verifica que sea una URL de artículo válida
                        if not re.search(r'n\d+$', url):
                            continue
                        
                        # Extrae el ID del artículo de la URL
                        article_id = re.search(r'n(\d+)$', url).group(1)
                        
                        found_articles = True
                        
                        # Obtiene el título del enlace
                        titulo = link.get_text().strip()
                        if not titulo:
                            # Si no hay texto en el enlace, busca en elementos hijos
                            title_element = link.find('h2') or link.find('h3') or link.find(class_='title')
                            if title_element:
                                titulo = title_element.get_text().strip()
                        
                        if not titulo:
                            continue
                        
                        # Scrapea la página individual del artículo para más detalles
                        try:
                            print(f"🔍 Scrapeando artículo: {url}")
                            nota_resp = requests.get(url, headers=headers, timeout=10)
                            nota_resp.raise_for_status()
                            nota_soup = BeautifulSoup(nota_resp.text, "html.parser")
                            
                            # Intenta obtener la fecha del artículo
                            fecha = self._extract_date(nota_soup, url)
                            
                            # Si el artículo es anterior a la fecha límite, terminar
                            if self.fecha_limite and fecha and fecha < self.fecha_limite:
                                print(f"📅 Se alcanzó la fecha límite ({self.fecha_limite}), finalizando búsqueda")
                                seguir = False
                                break
                            
                            # Intenta obtener el contenido del artículo
                            contenido, contenido_crudo = self._extract_content(nota_soup)
                            
                            # Obtiene el título final desde la página del artículo
                            titulo_final = self._extract_title(nota_soup, titulo)
                            
                            noticia_data = {
                                "titulo": titulo_final,
                                "contenido": contenido,
                                "contenido_crudo": contenido_crudo,
                                "fecha": fecha or datetime.date.today(),
                                "url": url,
                                "media_name": self.media_name
                            }
                            
                            if self._guardar_noticia(db, noticia_data):
                                noticias_guardadas += 1
                            
                            # Espera entre requests de artículos individuales
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f"❌ Error scraping artículo individual {url}: {str(e)}")
                            db.rollback()
                            continue
                    
                    except Exception as e:
                        print(f"❌ Error procesando artículo: {str(e)}")
                        continue
                
                if not found_articles:
                    print(f"🤷 No se encontraron artículos válidos en la página {pagina}")
                
                pagina += 1
                time.sleep(3)  # Espera entre páginas
                
            except Exception as e:
                print(f"❌ Error scraping TodoJujuy: {e}")
                break
                
        return noticias_guardadas
    
    def _extract_title(self, soup, fallback_title):
        """Extrae el título del artículo desde el HTML"""
        try:
            # Busca el título en el h1 principal
            title_element = soup.find('h1', class_='news-headline__title')
            if title_element:
                return title_element.get_text().strip()
            
            # Busca en el title del head
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text().strip()
                if title_text and title_text != fallback_title:
                    return title_text
            
            # Busca en otros elementos de título
            title_selectors = [
                'h1',
                '.article-title',
                '.news-title',
                '.headline'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title_text = title_element.get_text().strip()
                    if title_text:
                        return title_text
            
            return fallback_title
            
        except Exception as e:
            print(f"⚠️ Error extrayendo título: {e}")
            return fallback_title
    
    def _extract_date(self, soup, url):
        """Extrae la fecha del artículo desde el HTML o la URL"""
        try:
            # Busca la fecha en el elemento específico de TodoJujuy
            date_element = soup.find('span', class_='news-headline__date')
            if date_element:
                date_text = date_element.get_text().strip()
                # Formato: "8 de mayo de 2025 - 12:16"
                date_match = re.search(r'(\d+)\s+de\s+(\w+)\s+de\s+(\d{4})', date_text)
                if date_match:
                    dia = int(date_match.group(1))
                    mes_nombre = date_match.group(2).lower()
                    año = int(date_match.group(3))
                    
                    # Mapeo de nombres de meses a números
                    meses = {
                        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                    }
                    
                    if mes_nombre in meses:
                        mes = meses[mes_nombre]
                        return datetime.date(año, mes, dia)
            
            # Busca elementos de fecha comunes
            date_selectors = [
                'time',
                '.date',
                '.fecha',
                '.article-date',
                '[datetime]'
            ]
            
            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    # Intenta extraer fecha del atributo datetime
                    datetime_attr = date_element.get('datetime')
                    if datetime_attr:
                        try:
                            return datetime.datetime.fromisoformat(datetime_attr.split('T')[0]).date()
                        except:
                            pass
                    
                    # Intenta extraer fecha del texto
                    date_text = date_element.get_text().strip()
                    if date_text:
                        # Busca patrones de fecha comunes
                        date_patterns = [
                            r'(\d{1,2})/(\d{1,2})/(\d{4})',
                            r'(\d{1,2})-(\d{1,2})-(\d{4})',
                            r'(\d{4})-(\d{1,2})-(\d{1,2})'
                        ]
                        
                        for pattern in date_patterns:
                            match = re.search(pattern, date_text)
                            if match:
                                if len(match.groups()) == 3:
                                    if len(match.group(1)) == 4:  # Año primero
                                        return datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                                    else:  # Día primero
                                        return datetime.date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            
            # Si no se encuentra fecha en el HTML, usa la fecha actual
            return datetime.date.today()
            
        except Exception as e:
            print(f"⚠️ Error extrayendo fecha: {e}")
            return datetime.date.today()
    
    def _extract_content(self, soup):
        """Extrae el contenido limpio y el HTML crudo del artículo."""
        try:
            # El contenedor principal parece ser este
            content_container = soup.find('div', class_='col-12 col-lg-8')
            if not content_container:
                # Fallback si la estructura cambia
                content_container = soup.find('article') or soup.body

            raw_html = str(content_container)
            
            # Extraer párrafos solo del contenedor
            paragraphs = content_container.find_all('p')
            contenido_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                # Filtrar texto no deseado
                if text and 'Copyright ©' not in text and 'Sumate al Canal' not in text:
                    contenido_parts.append(text)
            
            clean_text = "\n\n".join(contenido_parts)
            
            return clean_text, raw_html

        except Exception as e:
            print(f"⚠️ Error extrayendo contenido: {e}")
            return "", "" 