from .base import BaseScraper
import requests
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin
import time
import json

class SomosJujuyScraper(BaseScraper):
    BASE_URL = "https://www.somosjujuy.com.ar"
    POLICIALES_URL = "https://www.somosjujuy.com.ar/policiales/"

    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.media_id = 'somosjujuy'

    def scrape(self, db) -> int:
        noticias_guardadas = 0
        pagina = 1
        seguir = True
        urls_vistas = set()
        last_page_content = None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        while seguir:
            url_pagina = f"{self.POLICIALES_URL}?page={pagina}"
            print(f"📄 Scraping página {pagina}: {url_pagina}")

            try:
                response = requests.get(url_pagina, headers=headers, timeout=10)
                response.raise_for_status()

                if response.text == last_page_content:
                    print("🛑 Contenido de página duplicado, finalizando paginación.")
                    break
                last_page_content = response.text

                soup = BeautifulSoup(response.text, "html.parser")

                # Los artículos están en elementos con la clase 'noti-box' o similar
                article_links = soup.select('a[href*="/policiales/"]')
                
                # Filtrar enlaces para que sean de noticias y únicos
                links_filtrados = []
                for link in article_links:
                    href = link.get('href')
                    if href and re.search(r'-n\d+$', href) and href not in urls_vistas:
                        links_filtrados.append(link)
                        urls_vistas.add(href)

                if not links_filtrados:
                    print(f"🤷 No se encontraron más artículos en la página {pagina}")
                    break

                for link in links_filtrados:
                    try:
                        url_articulo = urljoin(self.BASE_URL, link['href'])
                        
                        print(f"🔍 Scrapeando artículo: {url_articulo}")
                        nota_resp = requests.get(url_articulo, headers=headers, timeout=10)
                        nota_resp.raise_for_status()
                        nota_soup = BeautifulSoup(nota_resp.text, "html.parser")

                        # Extracción de datos con JSON-LD para mayor precisión
                        json_ld_scripts = nota_soup.find_all('script', type='application/ld+json')
                        article_data = None
                        for script in json_ld_scripts:
                            data = json.loads(script.string)
                            if isinstance(data, dict) and data.get('@type') == 'NewsArticle':
                                article_data = data
                                break
                        
                        if not article_data:
                            print(f"⚠️ No se encontró JSON-LD para el artículo: {url_articulo}")
                            continue

                        fecha = self._extract_date(article_data)
                        
                        if self.fecha_limite and fecha and fecha < self.fecha_limite:
                            print(f"📅 Se alcanzó la fecha límite ({self.fecha_limite}), finalizando búsqueda")
                            seguir = False
                            break

                        titulo = self._extract_title(article_data, nota_soup)
                        contenido, contenido_crudo = self._extract_content(nota_soup)

                        noticia = {
                            "titulo": titulo,
                            "contenido": contenido,
                            "contenido_crudo": contenido_crudo,
                            "fecha": fecha,
                            "url": url_articulo,
                            "media_id": self.media_id
                        }
                        
                        from app.db import Noticia
                        noticia_obj = Noticia(**noticia, es_accidente_transito=None)
                        db.add(noticia_obj)
                        db.commit()
                        noticias_guardadas += 1
                        print(f"✅ Artículo extraído y guardado: {titulo}")
                        
                        time.sleep(2)

                    except Exception as e:
                        print(f"❌ Error procesando artículo: {str(e)}")
                        continue
                
                if not seguir:
                    break

                pagina += 1
                time.sleep(3)

            except Exception as e:
                print(f"❌ Error scraping SomosJujuy: {e}")
                break
                
        return noticias_guardadas

    def _extract_title(self, data, soup):
        if data.get('headline'):
            return data['headline']
        title_tag = soup.find('h1', class_='tit-ficha')
        if title_tag:
            return title_tag.text.strip()
        return "Título no encontrado"

    def _extract_date(self, data):
        date_str = data.get('datePublished')
        if date_str:
            return datetime.datetime.fromisoformat(date_str).date()
        return datetime.date.today()

    def _extract_content(self, soup):
        """Extrae el contenido limpio y el HTML crudo del artículo."""
        try:
            content_div = soup.find('article', class_='content')
            if content_div:
                raw_html = str(content_div)
                paragraphs = content_div.find_all('p')
                clean_text = "\n\n".join(p.get_text().strip() for p in paragraphs)
                return clean_text, raw_html
            return "", ""
        except Exception as e:
            print(f"⚠️ Error extrayendo contenido: {e}")
            return "", "" 