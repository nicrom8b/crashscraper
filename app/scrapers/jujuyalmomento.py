import json
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.scrapers.base import BaseScraper
from app.db import Noticia

class JujuyAlMomentoScraper(BaseScraper):
    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.base_url = "https://www.jujuyalmomento.com"
        self.pagina_url_template = "https://www.jujuyalmomento.com/contenidos/policiales.html?page={page}"
        self.media_name = 'jujuyalmomento'

    def scrape(self, db) -> int:
        print(f" scraping {self.media_name}")
        pagina = 1
        noticias_guardadas = 0
        urls_vistas = set()
        
        while True:
            # La página 1 no usa el parámetro `page`
            if pagina == 1:
                url_pagina = "https://www.jujuyalmomento.com/contenidos/policiales.html"
            else:
                url_pagina = self.pagina_url_template.format(page=pagina)
            
            print(f"📄 Scraping página {pagina}: {url_pagina}")
            
            try:
                page_content = self._get_page_content(url_pagina)
                if not page_content:
                    print(f"🤷 No se pudo obtener contenido de la página {pagina}, finalizando.")
                    break

                print(f"✅ Página {pagina} obtenida exitosamente (tamaño: {len(page_content)} caracteres)")

                soup = BeautifulSoup(page_content, "html.parser")
                
                article_links = soup.select('a[href*="-n"]')
                current_page_urls = set()
                for link in article_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        current_page_urls.add(full_url)
                
                nuevas_urls = current_page_urls - urls_vistas
                
                print(f"📊 Página {pagina}: {len(current_page_urls)} URLs encontradas, {len(nuevas_urls)} nuevas")

                if not nuevas_urls:
                    print(f"🤷 No se encontraron más artículos nuevos en la página {pagina}, finalizando.")
                    break
                
                for url in nuevas_urls:
                    if url in urls_vistas:
                        continue
                    urls_vistas.add(url)
                    
                    print(f"🔍 Scrapeando artículo: {url}")
                    article_content = self._get_page_content(url)
                    if not article_content:
                        continue
                    
                    datos_articulo = self._scrape_article(url, article_content)
                    if not datos_articulo:
                        continue

                    # Chequeo de fecha límite
                    if self.fecha_limite and datos_articulo['fecha'].date() < self.fecha_limite:
                        print(f"📅 Se alcanzó la fecha límite ({self.fecha_limite}), finalizando búsqueda.")
                        return noticias_guardadas

                    # Guardar en DB
                    datos_articulo['media_name'] = self.media_name
                    if self._guardar_noticia(db, datos_articulo):
                        noticias_guardadas += 1

                    time.sleep(1)

                pagina += 1
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error en la página {pagina}: {e}")
                break
        
        return noticias_guardadas


    def _get_page_content(self, url: str):
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"❌ Error al obtener la página {url}: {e}")
            return None

    def _scrape_article(self, url: str, page_content: str):
        soup = BeautifulSoup(page_content, "html.parser")
        
        # Buscar el contenido del artículo específicamente
        article_content = soup.find('article', class_='article-body') or soup.find('div', class_='article-content')
        if article_content:
            contenido_crudo = str(article_content)
        else:
            # Fallback: usar solo el body si no se encuentra el contenido específico
            body = soup.find('body')
            contenido_crudo = str(body) if body else ''

        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if not script_tag:
            print(f"⚠️ No se encontró el tag script ld+json en {url}")
            return None

        try:
            json_data = json.loads(script_tag.string)
            news_article_data = None
            if isinstance(json_data, list):
                news_article_data = next((item for item in json_data if item.get('@type') == 'NewsArticle'), None)
            elif isinstance(json_data, dict) and json_data.get('@type') == 'NewsArticle':
                news_article_data = json_data
            
            if not news_article_data:
                print(f"⚠️ No se encontró el objeto NewsArticle en el JSON-LD de {url}")
                return None

            titulo = news_article_data.get('headline')
            fecha_str = news_article_data.get('datePublished')
            contenido = news_article_data.get('articleBody')

            if not all([titulo, fecha_str, contenido]):
                print(f"⚠️ Faltan datos en el JSON-LD de {url}")
                return None

            fecha = datetime.fromisoformat(fecha_str)

            return {
                'url': url,
                'titulo': titulo.strip(),
                'fecha': fecha,
                'contenido': contenido.strip(),
                'contenido_crudo': contenido_crudo,
            }

        except (json.JSONDecodeError, AttributeError, TypeError, StopIteration) as e:
            print(f"❌ Error al parsear JSON-LD de {url}: {e}")
            return None

class JujuyAlMomentoTagScraper(BaseScraper):
    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.base_url = "https://www.jujuyalmomento.com"
        self.media_name = 'jujuyalmomento'
        # Lista de etiquetas/slugs para scrapear
        self.tags = [
            "siniestro-a421",
            "choque-a8930", 
            "siniestro-vial-a3204",
            "vuelco-a12625"
        ]

    def scrape(self, db) -> int:
        total_guardadas = 0
        for tag in self.tags:
            print(f"\n🏷️ Scrapeando etiqueta: {tag}")
            guardadas = self._scrape_tag(tag, db)
            print(f"✅ Total guardadas para '{tag}': {guardadas}")
            total_guardadas += guardadas
        return total_guardadas

    def _scrape_tag(self, tag, db):
        pagina = 1
        noticias_guardadas = 0
        urls_vistas = set()
        while True:
            if pagina == 1:
                url_pagina = f"{self.base_url}/{tag}"
            else:
                url_pagina = f"{self.base_url}/{tag}/{pagina-1}"
            print(f"📄 Scraping página {pagina}: {url_pagina}")
            try:
                page_content = self._get_page_content(url_pagina)
                if not page_content:
                    print(f"🤷 No se pudo obtener contenido de la página {pagina}, finalizando etiqueta '{tag}'.")
                    break
                print(f"✅ Página {pagina} obtenida exitosamente (tamaño: {len(page_content)} caracteres)")
                soup = BeautifulSoup(page_content, "html.parser")
                article_links = soup.select('a[href*="-n"]')
                current_page_urls = set()
                for link in article_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        current_page_urls.add(full_url)
                nuevas_urls = current_page_urls - urls_vistas
                print(f"📊 Página {pagina}: {len(current_page_urls)} URLs encontradas, {len(nuevas_urls)} nuevas")
                if not nuevas_urls:
                    print(f"🤷 No se encontraron más artículos nuevos en la página {pagina}, finalizando etiqueta '{tag}'.")
                    break
                for url in nuevas_urls:
                    if url in urls_vistas:
                        continue
                    urls_vistas.add(url)
                    print(f"🔍 Scrapeando artículo: {url}")
                    article_content = self._get_page_content(url)
                    if not article_content:
                        continue
                    datos_articulo = self._scrape_article(url, article_content)
                    if not datos_articulo:
                        continue
                    if self.fecha_limite and datos_articulo['fecha'].date() < self.fecha_limite:
                        print(f"📅 Se alcanzó la fecha límite ({self.fecha_limite}), finalizando búsqueda para '{tag}'.")
                        return noticias_guardadas
                    datos_articulo['media_name'] = self.media_name
                    if self._guardar_noticia(db, datos_articulo):
                        noticias_guardadas += 1
                    time.sleep(1)
                pagina += 1
                time.sleep(2)
            except Exception as e:
                print(f"❌ Error en la página {pagina} de '{tag}': {e}")
                break
        return noticias_guardadas

    def _get_page_content(self, url: str):
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"❌ Error al obtener la página {url}: {e}")
            return None

    def _scrape_article(self, url: str, page_content: str):
        soup = BeautifulSoup(page_content, "html.parser")
        article_content = soup.find('article', class_='article-body') or soup.find('div', class_='article-content')
        if article_content:
            contenido_crudo = str(article_content)
        else:
            body = soup.find('body')
            contenido_crudo = str(body) if body else ''
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if not script_tag:
            print(f"⚠️ No se encontró el tag script ld+json en {url}")
            return None
        try:
            json_data = json.loads(script_tag.string)
            news_article_data = None
            if isinstance(json_data, list):
                news_article_data = next((item for item in json_data if item.get('@type') == 'NewsArticle'), None)
            elif isinstance(json_data, dict) and json_data.get('@type') == 'NewsArticle':
                news_article_data = json_data
            if not news_article_data:
                print(f"⚠️ No se encontró el objeto NewsArticle en el JSON-LD de {url}")
                return None
            titulo = news_article_data.get('headline')
            fecha_str = news_article_data.get('datePublished')
            contenido = news_article_data.get('articleBody')
            if not all([titulo, fecha_str, contenido]):
                print(f"⚠️ Faltan datos en el JSON-LD de {url}")
                return None
            fecha = datetime.fromisoformat(fecha_str)
            return {
                'url': url,
                'titulo': titulo.strip(),
                'fecha': fecha,
                'contenido': contenido.strip(),
                'contenido_crudo': contenido_crudo,
            }
        except (json.JSONDecodeError, AttributeError, TypeError, StopIteration) as e:
            print(f"❌ Error al parsear JSON-LD de {url}: {e}")
            return None 