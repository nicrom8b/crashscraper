from .base import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin
import time

class InformateSaltaScraper(BaseScraper):
    BASE_URL = "https://informatesalta.com.ar"
    POLICIALES_URL = "https://informatesalta.com.ar/categoria/13/policiales"
    AJAX_URL = "https://informatesalta.com.ar/default/listar_contenido"
    CATEGORY_ID = 13

    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.media_name = 'informate_salta'

    def scrape(self, db) -> int:
        noticias_guardadas = 0
        pagina = 1
        seguir = True
        urls_vistas = set()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        while seguir:
            try:
                if pagina == 1:
                    # La primera página se obtiene con GET de la URL principal
                    url_pagina = self.POLICIALES_URL
                    print(f"📄 Scraping página 1: {url_pagina}")
                    response = requests.get(url_pagina, headers=headers, timeout=15)
                else:
                    # Las páginas siguientes se obtienen con GET al endpoint de paginación
                    print(f"📄 Scraping página {pagina} (AJAX GET)...")
                    # El parámetro es 'p', no 'pagina'
                    params = {'categoria': self.CATEGORY_ID, 'p': pagina}
                    response = requests.get(self.AJAX_URL, headers=headers, params=params, timeout=15)

                response.raise_for_status()
                
                # En este sitio, si la página no existe, no da 404, devuelve la portada.
                # Verificamos si la URL de respuesta es la misma que pedimos.
                if response.history and response.url != self.POLICIALES_URL:
                    print(f"🤷 La página {pagina} redirigió a {response.url}. Probablemente no existe. Finalizando.")
                    break

                # Si la respuesta está vacía (suele pasar al final de la paginación), detenemos
                if not response.text.strip():
                    print(f"🤷 No se recibió contenido en la página {pagina}. Finalizando.")
                    break
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Buscar artículos en la página
                articles = soup.find_all('article', class_='post post__noticia')
                
                if not articles:
                    print(f"🤷 No se encontraron más artículos en la página {pagina}. Finalizando.")
                    break

                found_articles_on_page = False
                
                for article in articles:
                    try:
                        # Buscar el enlace del artículo
                        link_element = article.find('a', class_='post__imagen')
                        if not link_element:
                            continue
                            
                        url = urljoin(self.BASE_URL, link_element['href'])
                        
                        # Verificar que no se haya procesado ya
                        if url in urls_vistas:
                            continue
                        urls_vistas.add(url)
                        
                        # Extraer título
                        title_element = article.find('h2', class_='post__titulo')
                        if not title_element:
                            continue
                            
                        titulo = title_element.get_text().strip()
                        if not titulo:
                            continue
                        
                        # Extraer fecha
                        fecha_element = article.find('span', class_='post__fecha')
                        if fecha_element:
                            fecha_texto = fecha_element.get_text().strip()
                            # Formato: DD/MM/YYYY
                            try:
                                day, month, year = map(int, fecha_texto.split('/'))
                                article_date = datetime.date(year, month, day)
                            except ValueError:
                                # Si hay error en el formato, intentar otros o usar hoy
                                print(f"⚠️  Formato de fecha no reconocido: '{fecha_texto}'. Usando fecha actual.")
                                article_date = datetime.date.today()
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
                            db.rollback()
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
                print(f"❌ Error de red scraping Informate Salta (página {pagina}): {e}")
                break
            except Exception as e:
                print(f"❌ Error inesperado en página {pagina}: {e}")
                import traceback
                traceback.print_exc()
                break
                
        return noticias_guardadas

    def _extract_content(self, soup):
        """Extrae el contenido limpio y el HTML crudo del artículo."""
        try:
            # Buscar el contenido del artículo
            # En Informate Salta, el contenido principal está en el elemento principal
            content_selectors = [
                'main',
                '.main',
                'article',
                '.post__contenido',
                '.contenido',
                '.article-content'
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
                        not any(keyword in text.lower() for keyword in ['sesión', 'notificaciones', 'dólar', 'temas', 'publicidad', 'newsletter']) and
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