#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import locale
import time
from urllib.parse import urljoin
import dateparser

from app.scrapers.base import BaseScraper
from app.db import Noticia, get_db

class ElSubmarinoJujuyScraper(BaseScraper):
    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.media_name = 'elsubmarinojujuy'
        self.base_url = 'https://elsubmarinojujuy.com.ar'
        self.tag_url = 'https://elsubmarinojujuy.com.ar/tag/accidente/'
        
    def scrape(self, db):
        print(f"🚀 Scraping {self.media_name}")
        noticias_guardadas = 0
        page = 1
        
        while True:
            if page == 1:
                current_url = self.tag_url
            else:
                current_url = f"{self.tag_url}page/{page}/"

            print(f"📄 Scrapeando página {page}: {current_url}")
            
            try:
                response = requests.get(current_url, timeout=15)
                if response.status_code == 404:
                    print("🔚 No hay más páginas, se recibió un 404.")
                    break
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"❌ Error al solicitar la página {page}: {e}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            article_elements = soup.select('div.post-listing article.item-list')

            if not article_elements:
                print("🔚 No se encontraron más artículos en la página.")
                break

            detener_por_fecha = False
            for article_el in article_elements:
                url_articulo_tag = article_el.select_one('h2.post-title a')
                if not url_articulo_tag or not url_articulo_tag.has_attr('href'):
                    continue
                
                url_articulo = url_articulo_tag['href']

                # --- Extraer fecha primero para chequear límite ---
                date_tag = article_el.select_one('span.tie-date')
                fecha_texto = date_tag.get_text(strip=True) if date_tag else ''
                fecha_articulo = dateparser.parse(fecha_texto, languages=['es'])

                if self.fecha_limite and fecha_articulo and fecha_articulo.date() < self.fecha_limite:
                    print(f"📅 Se alcanzó la fecha límite ({fecha_articulo.date()}). Deteniendo.")
                    detener_por_fecha = True
                    break
                
                # --- Si la fecha es válida, proceder ---
                try:
                    datos_articulo = self._scrape_article(url_articulo)
                    if datos_articulo:
                        datos_articulo['media_name'] = self.media_name
                        if self._guardar_noticia(db, datos_articulo):
                            noticias_guardadas += 1
                except Exception as e:
                    print(f"❌ Error scrapeando artículo {url_articulo}: {e}")
                    db.rollback()

                time.sleep(1) 

            if detener_por_fecha:
                break
            
            page += 1
        
        print(f"✅ Scraping completado para {self.media_name}. Total de noticias guardadas: {noticias_guardadas}")
        return noticias_guardadas

    def _scrape_article(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Título ---
            titulo_tag = soup.select_one('h1.post-title')
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else 'Sin Título'

            # --- Fecha ---
            fecha_tag = soup.select_one('span.tie-date')
            fecha_texto = fecha_tag.get_text(strip=True) if fecha_tag else ''
            fecha_articulo = dateparser.parse(fecha_texto, languages=['es'])
            
            # --- Contenido ---
            contenido_tag = soup.select_one('div.entry')
            contenido = ''
            if contenido_tag:
                parrafos = contenido_tag.find_all('p')
                contenido = '\n'.join([p.get_text(strip=True) for p in parrafos])
            
            contenido_crudo = response.text

            return {
                "titulo": titulo,
                "contenido": contenido,
                "url": url,
                "fecha": fecha_articulo.date() if fecha_articulo else None,
                "contenido_crudo": contenido_crudo[:60000]
            }
        
        except requests.RequestException as e:
            print(f"❌ Error al solicitar artículo {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error procesando artículo {url}: {e}")
            return None

if __name__ == '__main__':
    # Script de prueba
    db_session = next(get_db())
    # Poner una fecha límite de hace 30 días para la prueba
    fecha_limite_prueba = datetime.now().date() - timedelta(days=30)
    scraper = ElSubmarinoJujuyScraper(fecha_limite=fecha_limite_prueba)
    scraper.scrape(db_session)
    db_session.close() 