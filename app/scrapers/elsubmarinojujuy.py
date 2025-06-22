#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import locale
import time
from urllib.parse import urljoin

from app.scrapers.base import BaseScraper
from app.db import Noticia, get_db

class ElSubmarinoJujuyScraper(BaseScraper):
    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.media_id = 'elsubmarinojujuy'
        self.base_url = 'https://elsubmarinojujuy.com.ar'
        self.tag_url = 'https://elsubmarinojujuy.com.ar/tag/accidente/'
        
        # Intentar configurar el localismo para español para parsear los meses
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'es_AR.UTF-8')
            except locale.Error:
                print("⚠️ No se pudo configurar el localismo a español. El parseo de fechas puede fallar.")

    def scrape(self, db):
        print(f"🚀 Scraping {self.media_id}")
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
                fecha_articulo = None
                if fecha_texto:
                    try:
                        fecha_articulo = datetime.strptime(fecha_texto, '%A, %d %B, %Y')
                    except ValueError:
                        pass # La fecha se parseará de nuevo en _scrape_article

                if self.fecha_limite and fecha_articulo and fecha_articulo.date() < self.fecha_limite:
                    print(f"📅 Se alcanzó la fecha límite ({fecha_articulo.date()}). Deteniendo.")
                    detener_por_fecha = True
                    break
                
                # --- Si la fecha es válida, proceder ---
                if db.query(Noticia).filter(Noticia.url == url_articulo).first():
                    print(f"⏭️ Artículo ya existe: {url_articulo}")
                    continue

                try:
                    articulo_guardado, _ = self._scrape_article(url_articulo, db)
                    if articulo_guardado:
                        noticias_guardadas += 1
                        print(f"✅ Artículo guardado: {url_articulo}")
                except Exception as e:
                    print(f"❌ Error scrapeando artículo {url_articulo}: {e}")

                time.sleep(1) 

            if detener_por_fecha:
                break
            
            page += 1
        
        print(f"✅ Scraping completado para {self.media_id}. Total de noticias guardadas: {noticias_guardadas}")
        return noticias_guardadas

    def _scrape_article(self, url, db):
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
            fecha_articulo = None
            if fecha_texto:
                try:
                    # Formato: "viernes, 2 mayo, 2025"
                    fecha_articulo = datetime.strptime(fecha_texto, '%A, %d %B, %Y')
                except ValueError as e:
                    print(f"⚠️ No se pudo parsear la fecha '{fecha_texto}': {e}")

            # --- Contenido ---
            contenido_tag = soup.select_one('div.entry')
            contenido = ''
            if contenido_tag:
                parrafos = contenido_tag.find_all('p')
                contenido = '\n'.join([p.get_text(strip=True) for p in parrafos])
            
            contenido_crudo = response.text

            # Guardar en DB
            noticia = Noticia(
                titulo=titulo,
                contenido=contenido,
                url=url,
                fecha=fecha_articulo,
                contenido_crudo=contenido_crudo[:60000],
                media_id=self.media_id
            )
            db.add(noticia)
            db.commit()

            return True, fecha_articulo
        
        except requests.RequestException as e:
            print(f"❌ Error al solicitar artículo {url}: {e}")
            return False, None
        except Exception as e:
            print(f"❌ Error procesando artículo {url}: {e}")
            db.rollback()
            return False, None

if __name__ == '__main__':
    # Script de prueba
    db_session = next(get_db())
    # Poner una fecha límite de hace 30 días para la prueba
    fecha_limite_prueba = datetime.now().date() - timedelta(days=30)
    scraper = ElSubmarinoJujuyScraper(fecha_limite=fecha_limite_prueba)
    scraper.scrape(db_session)
    db_session.close() 