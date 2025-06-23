import json
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.scrapers.base import BaseScraper
from app.db import Noticia

class JujuyDiceScraper(BaseScraper):
    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.base_url = "https://www.jujuydice.com.ar"
        self.pagina_url_template = "https://www.jujuydice.com.ar/noticias/pagina-{page}"
        self.media_name = 'jujuydice'

    def scrape(self, db) -> int:
        print(f"🚀 Scraping {self.media_name}")
        pagina = 1
        noticias_guardadas = 0
        urls_vistas = set()
        
        while True:
            url_pagina = self.pagina_url_template.format(page=pagina)
            print(f"📄 Procesando página {pagina}: {url_pagina}")
            
            try:
                response = requests.get(url_pagina, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Buscar todos los artículos en la página
                articulos = soup.find_all("article", class_="noticia")
                
                if not articulos:
                    print(f"❌ No se encontraron artículos en la página {pagina}")
                    break
                
                print(f"📰 Encontrados {len(articulos)} artículos en la página {pagina}")
                
                articulos_procesados = 0
                articulos_antiguos = 0
                
                for articulo in articulos:
                    try:
                        # Extraer URL del artículo
                        link_element = articulo.find("h2", class_="h2").find("a")
                        if not link_element:
                            continue
                        url_articulo = link_element.get("href")
                        if not url_articulo:
                            continue
                        if url_articulo.startswith("/"):
                            url_articulo = urljoin(self.base_url, url_articulo)
                        if url_articulo in urls_vistas:
                            continue
                        urls_vistas.add(url_articulo)

                        # Extraer contenido, título y fecha del artículo individual
                        contenido, titulo, fecha_articulo, contenido_crudo = self._extraer_contenido_articulo(url_articulo)
                        if not titulo:
                            # Fallback: usar el título de la lista
                            titulo_element = link_element.find("span", attrs={"itemprop": "headline"})
                            titulo = titulo_element.get_text(strip=True) if titulo_element else ""
                        if not fecha_articulo:
                            # Fallback: usar la fecha de la lista
                            fecha_element = articulo.find("span", class_="fecha")
                            fecha_texto = fecha_element.get_text(strip=True).replace(".", "") if fecha_element else ""
                            fecha_articulo = self._parsear_fecha(fecha_texto)
                        if not contenido:
                            contenido = ""
                        if not titulo or not fecha_articulo:
                            continue
                        if self.fecha_limite and fecha_articulo < self.fecha_limite:
                            articulos_antiguos += 1
                            if articulos_antiguos >= 3:
                                print(f"🛑 Demasiados artículos antiguos, deteniendo scraping en página {pagina}")
                                return noticias_guardadas
                            continue

                        noticia_data = {
                            "titulo": titulo,
                            "contenido": contenido,
                            "url": url_articulo,
                            "fecha": fecha_articulo,
                            "contenido_crudo": contenido_crudo,
                            "media_name": self.media_name
                        }
                        
                        if self._guardar_noticia(db, noticia_data):
                            noticias_guardadas += 1
                            articulos_procesados += 1
                        
                    except Exception as e:
                        print(f"❌ Error procesando artículo: {e}")
                        db.rollback()
                        continue
                print(f"📊 Página {pagina}: {articulos_procesados} artículos guardados, {articulos_antiguos} artículos antiguos")
                if articulos_procesados == 0:
                    print(f"🛑 No se procesaron artículos en la página {pagina}, deteniendo")
                    break
                pagina += 1
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error procesando página {pagina}: {e}")
                break
        print(f"🎉 Scraping completado. Se guardaron {noticias_guardadas} noticias.")
        return noticias_guardadas

    def _parsear_fecha(self, fecha_texto):
        """Parsea la fecha del formato DD/MM/YYYY"""
        try:
            if not fecha_texto:
                return None
            return datetime.strptime(fecha_texto, "%d/%m/%Y").date()
        except ValueError:
            return None

    def _extraer_contenido_articulo(self, url_articulo):
        """Extrae el contenido completo de un artículo individual"""
        try:
            response = requests.get(url_articulo, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extraer título
            titulo = ""
            h1 = soup.find("h1")
            if h1:
                titulo = h1.get_text(strip=True)

            # Extraer fecha
            fecha = None
            fecha_span = soup.find("span", class_="fecha")
            if fecha_span:
                fecha_texto = fecha_span.get_text(strip=True).replace(".", "")
                fecha = self._parsear_fecha(fecha_texto)

            # Extraer contenido principal
            contenido_element = soup.find("div", class_="cda", itemprop="articleBody")
            if contenido_element:
                contenido = contenido_element.get_text(separator="\n", strip=True)
            else:
                contenido = ""

            # Limitar el tamaño de contenido_crudo
            contenido_crudo = response.text[:60000]

            return contenido, titulo, fecha, contenido_crudo
        except Exception as e:
            print(f"❌ Error extrayendo contenido de {url_articulo}: {e}")
            return "", "", None, "" 