from .base import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin
import time

class ElTribunoSaltaScraper(BaseScraper):
    BASE_URL = "https://www.eltribuno.com"
    POLICIALES_URL = "https://www.eltribuno.com/seccion/policiales"

    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.media_name = 'eltribuno_salta'

    def scrape(self, db) -> int:
        noticias_guardadas = 0
        pagina = 1
        seguir = True
        urls_vistas = set()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        while seguir:
            url_pagina = f"{self.POLICIALES_URL}/{pagina}" if pagina > 1 else self.POLICIALES_URL
            print(f"📄 Scraping página {pagina}: {url_pagina}")
            
            try:
                response = requests.get(url_pagina, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Buscar enlaces de artículos en la página
                # Los artículos están en enlaces que contienen el patrón de fecha
                article_links = soup.find_all('a', href=re.compile(r'/policiales/\d{4}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}-'))
                
                if not article_links:
                    print(f"🤷 No se encontraron más artículos en la página {pagina}")
                    break

                found_articles = False
                
                for link in article_links:
                    try:
                        url = urljoin(self.BASE_URL, link['href'])
                        
                        # Verificar que no se haya procesado ya
                        if url in urls_vistas:
                            continue
                        urls_vistas.add(url)
                        
                        # Extrae la fecha del enlace
                        # Formato: /policiales/2025-6-20-13-38-0-titulo-de-la-noticia
                        date_match = re.search(r'/policiales/(\d{4})-(\d{1,2})-(\d{1,2})-\d{1,2}-\d{1,2}-\d{1,2}-', url)
                        if not date_match:
                            continue
                            
                        year, month, day = date_match.groups()
                        article_date = datetime.date(int(year), int(month), int(day))
                        
                        # Si el artículo es anterior a la fecha límite, terminar
                        if self.fecha_limite and article_date < self.fecha_limite:
                            print(f"📅 Se alcanzó la fecha límite ({self.fecha_limite}), finalizando búsqueda")
                            seguir = False
                            break
                        
                        found_articles = True
                        
                        # Obtiene el título del enlace
                        titulo = link.get_text().strip()
                        if not titulo:
                            # Si no hay texto en el enlace, busca en elementos hijos
                            title_element = link.find('h2') or link.find('h3') or link.find(class_='title')
                            if title_element:
                                titulo = title_element.get_text().strip()
                        
                        # Si aún no hay título, intentar extraerlo de la URL
                        if not titulo:
                            # Extraer título de la URL: /policiales/2025-6-20-13-38-0-titulo-de-la-noticia
                            url_parts = url.split('/')[-1].split('-')
                            if len(url_parts) >= 7:
                                # Saltar los 6 primeros elementos (fecha) y tomar el resto como título
                                title_parts = url_parts[6:]
                                titulo = ' '.join(title_parts).replace('-', ' ').title()
                        
                        if not titulo:
                            continue
                        
                        # Scrapea la página individual del artículo para más detalles
                        try:
                            print(f"🔍 Scrapeando artículo: {url}")
                            nota_resp = requests.get(url, headers=headers, timeout=10)
                            nota_resp.raise_for_status()
                            nota_soup = BeautifulSoup(nota_resp.text, "html.parser")
                            
                            contenido, contenido_crudo = self._extract_content(nota_soup)

                            # Construir la fecha desde las partes extraídas de la URL
                            fecha = article_date
                            noticia_data = {
                                "titulo": titulo,
                                "contenido": contenido,
                                "contenido_crudo": contenido_crudo,
                                "fecha": fecha,
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
                print(f"❌ Error scraping El Tribuno Salta: {e}")
                break
                
        return noticias_guardadas

    def _extract_content(self, soup):
        """Extrae el contenido limpio y el HTML crudo del artículo."""
        try:
            # Buscar el contenido del artículo principal
            # El contenido principal está en el elemento <article>
            article_content = soup.find('article')
            
            if not article_content:
                # Fallback: buscar por clases específicas de El Tribuno
                article_content = soup.find(class_='nota--gral')
            
            if article_content:
                raw_html = str(article_content)
                
                # Extraer párrafos del contenido principal
                paragraphs = article_content.find_all('p')
                clean_text = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                # Si no hay párrafos, intentar extraer texto del contenido completo
                if not clean_text:
                    clean_text = article_content.get_text().strip()
                
                return clean_text, raw_html
            
            # Fallback: buscar todos los párrafos y tomar los primeros que parezcan del artículo principal
            all_paragraphs = soup.find_all('p')
            if all_paragraphs:
                # Filtrar párrafos que parezcan del artículo principal (excluir navegación, publicidad, etc.)
                main_paragraphs = []
                for p in all_paragraphs:
                    text = p.get_text().strip()
                    # Excluir párrafos que parezcan navegación o publicidad
                    if (text and 
                        len(text) > 20 and  # Párrafos largos
                        not any(keyword in text.lower() for keyword in ['sesión', 'notificaciones', 'dólar', 'temas', 'publicidad']) and
                        not text.startswith('¿') and  # Excluir preguntas de navegación
                        not text.isupper()):  # Excluir texto en mayúsculas (títulos de navegación)
                        main_paragraphs.append(text)
                
                if main_paragraphs:
                    clean_text = "\n\n".join(main_paragraphs[:10])  # Tomar los primeros 10 párrafos
                    raw_html = str(soup.find('body'))  # HTML completo como fallback
                    return clean_text, raw_html
            
            return "", ""
        except Exception as e:
            print(f"⚠️  Error extrayendo contenido: {e}")
            return "", "" 