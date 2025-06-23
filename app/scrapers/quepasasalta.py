from .base import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin
import time
import json

class QuePasaSaltaScraper(BaseScraper):
    BASE_URL = "https://www.quepasasalta.com.ar"
    POLICIALES_URL = "https://www.quepasasalta.com.ar/seccion/policiales/"
    AJAX_URL = "https://www.quepasasalta.com.ar/0/seccion/list/ajax.vnc"
    CATEGORY_ID = 49  # ID for policiales section

    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.media_name = 'quepasasalta'

    def scrape(self, db) -> int:
        noticias_guardadas = 0
        pagina = 1
        seguir = True
        urls_vistas = set()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': self.POLICIALES_URL
        }

        while seguir:
            try:
                if pagina == 1:
                    # La primera página se obtiene con GET de la URL principal
                    url_pagina = self.POLICIALES_URL
                    print(f"📄 Scraping página 1: {url_pagina}")
                    response = requests.get(url_pagina, headers=headers, timeout=15)
                else:
                    # Las páginas siguientes se obtienen con POST al endpoint AJAX
                    print(f"📄 Scraping página {pagina} (AJAX POST)...")
                    
                    # Payload para la petición AJAX
                    payload = {
                        'id': self.CATEGORY_ID,
                        'page': pagina - 1,  # El AJAX usa 0-based indexing
                        'itemsPerPage': 21,
                        'pieceProperties': 'YUZobW1nQUM2MWM2ZVpodENXSlZyM2tMTU13TFNLSlBaaW5XYlJ4dFg3NG1UeXpLWFZyc1ZTOCt6bTVISVVpclpVVXAzMXdFK2xSbU5jQjJBR2NTckRwZktJNVdGL3NGT242VmJsTXJUZU5pRVcvU0dFWG1WQ2wxM0haQUtoem9LVWhwbkVnQnFBUTdPNUErVER0THB6aFNKOHNaV1BsUUkybkphbGR3SExnNkhIM0JBUUM5RHpwemh6MVZhUW5qYVExZ2xRdEx2Ujk0T0lCeVNXNE05R1FaZnBVZFhPa1RJM25NZmhScEcrY3hUQ2ZJUmgybEgzcDV6R2xWSlZIMkpsWnNuVm9hb0FobWZzbCtVamNQb3lGRU1zaEdIYVVmTkh6VmIxVTNINzl3WEhiY1VRN3JTblF1MXk0Yk9RVDVkMWgzaWgxWTkwMDRmWlFrU2pzRHRDWlVKcEZXQ2YxSVAzMlJMUVp4QStWaUdIWGJHbGl0QW04MXdHTkNQVkNvZmhJMHdSMU01VVo1TFpFakNDd1I1R0ZhTVlkY0NLMUhZV25ZTXcwN1F2UnVWQytaQ1FhcUhpd2p5MnNMT2x1bkxoOTdnbGhMcEJrMUxzcHRDM3dVNzI4Vll0RVFDL1pDWmpYVWVWTTZCcmh4VzNQTUZRL2lReTV0MkhJWk5BSHVLQTRqanhVZTRrTm5kNDhpWFhwTDRDNUFldG9BRXEwWmN5aWNLd3h4V09GNEdUZVRTUXI5WGp4KzMyVVVlRTc4TGxvdmlVOUU3bFE3TFpvNFdqSkErMkFGZXRsZUQ2RkxPMkhWYVFOcUY3UTVTQ2FXQUJMdldESW96VHNDT3h5bmJFOS95MTFGb0Y1bU5wcHZEVHdNNldKUllZeFZETGdNT25uV2VBd2xUTzg5RkhiTkdFS2xRbjBzMFRaZWV4dWdaUWdoa1RoVXBSUWtNTXhpVnpBYnN5UkRKcEVFVTZBRFlYUFdZbElpU3VSd0hHL0JEUWF6VW1ob3h6RVRjd0tzTmxZK2d3Y2RxVVY3SWMwc1VqOUl2VE5NTzRBTkFhNUFhRCtMWlVVdFYvVWdReU9XQzFEbUNDNTEyaWRQTmszaU13b3BpMG9jckJrcmI5OGtSU3BLNXlBVWI4SmREck5ST0dESE1rTjdBcTltWGo2QVZ4V3BSblV1Mm53Q04waStZVmdsMDBRZjRGNHRjWXQ4QkRaUnZ6ME1jNW9XQXJGTk15ZVNMaGg1QWZac0dIT2ZYRXIzUUM5d3dub0RhMUdrWkE1em53MFpyeHN2Y01KNkZ6UkdwV1FPZDV4SUZlQkJLWHVFSUY0c0JPZzZSV1dBV3gvcFJTODkwalpmTEFMb2JCbzF5aFVPNkJRaE5NcG5WMmtQK0RZYmE1VlZWYVFETkNiVVpsTi9BdlFuRm0zV1YxS21CMjF3a2owY1pWZmxKbGRrMzE1U3FVNHdOc2c4QkNRUXZtTkJmZHRVWDZWZElUclhKQWNvSEtvMkdTeVFBd0drSGk1MnpYb1VkRTNvSWt3OWtGb2U5MDAvY0lRa0h5aFUvUzRmWk5GUUh2Y2VQbithZXg4blV1cHNUajJFQkNuL0NXMUZtaWhNSTFMbU8wbzJrZ0FrNGdVd0ZKSjlVM0FIb0RZZWRNa05jUHNRUGtQS1BGbHdCL00zRVdxV0RYSHpCMzRZQUdrTlJ3L2tZU0o3eGw1c1lRdGtUZ0pxV2xGQjhUUnplb0lVT21zRkpCaFFkZzVDUUtCOUxUWFNIaTVxVkcwVVcyNGVTQmZwYlhJazJVOGtlVlU0Vnc0OFYxQkt2Q1UxTDlKY01uMWZQVk1PTDBoUVM3c3BKQ0xVV0RCNlhXMEtXR3dMSDFIdUtTUWkxRnN3YVZ3MVZSNHZHeDBZOW1oK2FwTkNQSHBLSTFzZkp3MFFBLzU4WldhTVJqOTJSbndLUUh3RlIxMy9LREEwbTE1bklRUnNWeEYwWEZnT3FqRTlZTmtVYW5VZExsdEVMVmhTRHFwb2FXRExIWGR5SDNnRkFYWUZERnFkWkc0MitJdHJJUUt4V2hZNEVFd05pMlFwWS8rVE9YbFc1MUFOUHhaTUU1cGxkaU9naUQ0dkJMSVBIRDVIVkJqVEpERnN1cEIvZFZ2eEdGZGdVRjBKem5JMU91eUNJbVZhdUFBVk0wbEdBTlFvSVNMdjNXTndSLzhRRlNSYkd4WFZlU0JtNzR0NWVrci9IQmMrVGhwRWhqMGdjN3llZXpVRjl4aFpZQjlCQWNnbmV5TzgxU01xV3FGQ1RYaE9EMC9aZEMwbjY1b3hkMHFyQkUxb1ZoWlUwU1I2TmFqQ2Fqa05wd2xjTDBFSVJjRjdLaWVnbkhwbUdiNUJGU01WUkVMU2ZDbzJ0NDkxTHdIcUIwcGdEa1pYem1kOFl2V0piMmhiczAwYlBoUkdVOFZnS1NHMnd5eHBYL0lYR21WQ0VrT01PMkltcnNZdE9CSDhEMVowQUJFY21uTXJMYXFMZkhSUDd4VVZPRWtKUU05ck1pbjFobkZoVVBWTFVHRllCUm5PUEd4NHBzOXBQUVM3U3dadFdRVWZ6bUoySmYrQmVEQmE1QnhaTzFSTUI1STNPSFh6aFc4cFhyNGNFMjVEVVJyUk1Hc3I0b1ErTVZYaFhWUWpDa2xiaTJnbFBxbUFMejFDc1JVZkxsTldCSmcyTlhEeDJHWnJYYXRjV20xWlcxTEtQRGczcVpGK0tnU3pSVmsrVUZsRTJqNDhNNm1DY21NYzV4Wk9kQjVhV3RGcWVHR2lnbjhwSEtBUFFIbFFTVkdZS0N3MXVzTnFKaEQ1U0VoMUUxOFBqbTUvTDY2T08ycE8$'
                    }
                    
                    response = requests.post(self.AJAX_URL, headers=headers, data=payload, timeout=15)

                response.raise_for_status()
                
                # Si la respuesta está vacía, detenemos
                if not response.text.strip():
                    print(f"🤷 No se recibió contenido en la página {pagina}. Finalizando.")
                    break
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Buscar artículos en la página
                # En Que Pasa Salta, los artículos están en elementos con clase específica
                articles = soup.find_all(['article', 'div'], class_=re.compile(r'(noticia|articulo|post|item)'))
                
                # Si no encontramos con las clases específicas, buscar por estructura
                if not articles:
                    articles = soup.find_all(['h2', 'h3'], class_=re.compile(r'(titulo|title)'))
                    if articles:
                        # Si encontramos títulos, tomar el contenedor padre
                        articles = [title.parent for title in articles]
                
                # Fallback: buscar cualquier elemento que contenga enlaces a artículos
                if not articles:
                    links = soup.find_all('a', href=re.compile(r'/nota/|/articulo/|/policiales/'))
                    articles = [link.parent for link in links if link.parent]
                
                if not articles:
                    print(f"🤷 No se encontraron más artículos en la página {pagina}. Finalizando.")
                    break

                found_articles_on_page = False
                
                for article in articles:
                    try:
                        # Buscar el enlace del artículo
                        link_element = article.find('a', href=True)
                        if not link_element:
                            continue
                            
                        url = urljoin(self.BASE_URL, link_element['href'])
                        
                        # Verificar que sea una URL válida de artículo
                        if not any(pattern in url for pattern in ['/nota/', '/articulo/', '/policiales/']):
                            continue
                        
                        # Verificar que no se haya procesado ya
                        if url in urls_vistas:
                            continue
                        urls_vistas.add(url)
                        
                        # Extraer título
                        title_element = article.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'(titulo|title)'))
                        if not title_element:
                            # Fallback: buscar cualquier elemento de título
                            title_element = article.find(['h1', 'h2', 'h3', 'h4'])
                        
                        if not title_element:
                            continue
                            
                        titulo = title_element.get_text().strip()
                        if not titulo:
                            continue
                        
                        # Extraer fecha
                        fecha_element = article.find(['span', 'time', 'div'], class_=re.compile(r'(fecha|date|time)'))
                        if fecha_element:
                            fecha_texto = fecha_element.get_text().strip()
                            # Intentar diferentes formatos de fecha
                            article_date = self._parse_date(fecha_texto)
                        else:
                            # Si no hay fecha, usar la de hoy y seguir
                            article_date = datetime.date.today()
                        
                        # Si el artículo es anterior a la fecha límite, terminar
                        if self.fecha_limite and article_date < self.fecha_limite:
                            print(f"📅 Se alcanzó la fecha límite ({self.fecha_limite}), finalizando búsqueda.")
                            seguir = False
                            break
                        
                        found_articles_on_page = True
                        
                        # Scrapea la página individual del artículo para más detalles
                        try:
                            print(f"🔍 Scrapeando artículo: {url}")
                            nota_resp = requests.get(url, headers=headers, timeout=10)
                            nota_resp.raise_for_status()
                            nota_soup = BeautifulSoup(nota_resp.text, "html.parser")
                            
                            contenido, contenido_crudo = self._extract_content(nota_soup)

                            noticia_data = {
                                "titulo": titulo,
                                "contenido": contenido,
                                "contenido_crudo": contenido_crudo,
                                "fecha": article_date,
                                "url": url,
                                "media_name": self.media_name
                            }
                            
                            if self._guardar_noticia(db, noticia_data):
                                noticias_guardadas += 1
                            
                            # Espera entre requests de artículos individuales
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f"❌ Error scraping artículo individual {url}: {str(e)}")
                            continue
                    
                    except Exception as e:
                        print(f"❌ Error procesando un artículo: {str(e)}")
                        continue
                
                if not found_articles_on_page:
                    print(f"🤷 No se encontraron artículos válidos en la página {pagina}. Puede ser el final.")
                
                # Si hemos llegado al final por la fecha, salimos del bucle principal
                if not seguir:
                    break
                
                pagina += 1
                time.sleep(3)  # Espera entre páginas
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de red scraping Que Pasa Salta (página {pagina}): {e}")
                break
            except Exception as e:
                print(f"❌ Error inesperado en página {pagina}: {e}")
                import traceback
                traceback.print_exc()
                break
                
        return noticias_guardadas

    def _parse_date(self, fecha_texto):
        """Parsea diferentes formatos de fecha."""
        try:
            # Formato: DD/MM/YYYY
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', fecha_texto):
                day, month, year = map(int, fecha_texto.split('/'))
                return datetime.date(year, month, day)
            
            # Formato: YYYY-MM-DD
            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', fecha_texto):
                year, month, day = map(int, fecha_texto.split('-'))
                return datetime.date(year, month, day)
            
            # Formato: DD de MMMM de YYYY
            meses = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            match = re.match(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', fecha_texto.lower())
            if match:
                day, month_name, year = match.groups()
                if month_name in meses:
                    return datetime.date(int(year), meses[month_name], int(day))
            
            # Si no se puede parsear, usar fecha actual
            print(f"⚠️  Formato de fecha no reconocido: '{fecha_texto}'. Usando fecha actual.")
            return datetime.date.today()
            
        except Exception as e:
            print(f"⚠️  Error parseando fecha '{fecha_texto}': {e}. Usando fecha actual.")
            return datetime.date.today()

    def _extract_content(self, soup):
        """Extrae el contenido limpio y el HTML crudo del artículo."""
        try:
            # Buscar el contenido del artículo
            content_selectors = [
                'main',
                '.main',
                'article',
                '.contenido',
                '.article-content',
                '.noticia-contenido',
                '.post-content',
                '.entry-content'
            ]
            
            article_content = None
            for selector in content_selectors:
                article_content = soup.select_one(selector)
                if article_content:
                    break
            
            if not article_content:
                # Fallback: buscar por párrafos
                paragraphs = soup.find_all('p')
                if paragraphs:
                    # Tomar el contenedor del primer párrafo
                    article_content = paragraphs[0].parent
            
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
                        not any(keyword in text.lower() for keyword in ['sesión', 'notificaciones', 'dólar', 'temas', 'publicidad', 'newsletter', 'comentarios']) and
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