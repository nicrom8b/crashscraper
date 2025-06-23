import json
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.scrapers.base import BaseScraper
from app.db import Noticia

class PregonScraper(BaseScraper):
    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
        self.base_url = "https://www.pregon.com.ar"
        self.seccion_url = "https://www.pregon.com.ar/Policial"
        self.ajax_endpoint = "https://www.pregon.com.ar/CalledConsultasExternas.php"
        self.media_name = 'pregon'

    def scrape(self, db) -> int:
        print(f"🚀 Scraping {self.media_name}")
        noticias_guardadas = 0
        urls_vistas = set()
        
        # Obtener la página inicial
        try:
            response = requests.get(self.seccion_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extraer URLs de artículos de la página inicial
            urls_articulos = self._extraer_urls_articulos(soup)
            
            # Procesar cada artículo inicial
            for url_articulo in urls_articulos:
                if url_articulo in urls_vistas:
                    continue
                    
                urls_vistas.add(url_articulo)
                print(f"🔍 Scrapeando artículo: {url_articulo}")
                
                # Extraer contenido del artículo
                contenido_articulo = self._extraer_contenido_articulo(url_articulo)
                
                if contenido_articulo:
                    titulo, contenido, fecha_articulo, contenido_crudo = contenido_articulo
                    
                    # Verificar si ya existe en la base de datos
                    if db.query(Noticia).filter(Noticia.url == url_articulo).first():
                        print(f"⏭️ Artículo ya existe: {titulo[:50]}...")
                        continue
                    
                    # Verificar fecha límite
                    if self.fecha_limite and fecha_articulo and fecha_articulo.date() < self.fecha_limite:
                        print(f"📅 Artículo muy antiguo ({fecha_articulo.date()}), deteniendo scraping")
                        return noticias_guardadas
                    
                    # Crear objeto Noticia
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
                
                time.sleep(1)  # Pausa entre requests
            
            # Usar el método "Ver Más" para cargar artículos más antiguos
            noticias_adicionales = self._cargar_mas_articulos_vermas(db, urls_vistas)
            noticias_guardadas += noticias_adicionales
            
        except Exception as e:
            print(f"❌ Error en scraping inicial: {e}")
        
        print(f"✅ Scraping completado. Total de noticias guardadas: {noticias_guardadas}")
        return noticias_guardadas

    def _extraer_urls_articulos(self, soup):
        """Extrae las URLs de los artículos de la página"""
        urls = []
        
        # Buscar enlaces de artículos
        enlaces = soup.find_all("h4", class_="titulo")
        for enlace in enlaces:
            link = enlace.find("a")
            if link and link.get("href"):
                url = link.get("href")
                if url.startswith("/"):
                    url = self.base_url + url
                urls.append(url)
        
        print(f"📄 Encontradas {len(urls)} URLs de artículos en la página inicial")
        return urls

    def _extraer_contenido_articulo(self, url_articulo):
        """Extrae el contenido completo de un artículo individual"""
        try:
            response = requests.get(url_articulo, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            if soup:
                raw_html = str(soup.find('body')) # Usar el cuerpo como fallback si no hay un article
            else:
                raw_html = ""
            
            # Extraer título
            titulo_element = soup.find("h1", class_="titulo") if soup else None
            titulo = titulo_element.get_text(strip=True) if titulo_element else ""

            # Extraer fecha
            fecha = None
            script_ld = soup.find("script", type="application/ld+json") if soup else None
            if script_ld:
                try:
                    json_data = json.loads(script_ld.string)
                    if isinstance(json_data, dict) and 'datePublished' in json_data:
                        fecha_str = json_data['datePublished'] # Formato: "17-06-2025"
                        if '-' in fecha_str and len(fecha_str.split('-')) == 3:
                            try:
                                dia, mes, anio = fecha_str.split('-')
                                fecha = datetime(int(anio), int(mes), int(dia))
                            except ValueError: pass
                except (json.JSONDecodeError, TypeError): pass
            
            # Extraer contenido principal
            texto_div = soup.find("div", class_="texto") if soup else None
            contenido = ""
            if texto_div:
                parrafos = texto_div.find_all("p")
                contenido = "\n\n".join([p.get_text(strip=True) for p in parrafos if p.get_text(strip=True)])

            if titulo and contenido:
                return titulo, contenido, fecha, raw_html[:60000]
            else:
                print(f"⚠️ No se pudo extraer contenido completo de: {url_articulo}")
                return None, None, None, None

        except Exception as e:
            print(f"❌ Error extrayendo artículo {url_articulo}: {e}")
            return None, None, None, None

    def _cargar_mas_articulos_vermas(self, db, urls_vistas):
        """Carga más artículos usando el método 'Ver Más' de manera iterativa"""
        noticias_adicionales = 0
        
        try:
            print("🔄 Cargando más artículos usando método 'Ver Más'...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/json',
                'Referer': self.seccion_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            content_ids = []
            for url in urls_vistas:
                if "/nota/" in url:
                    parts = url.split("/nota/")
                    if len(parts) > 1:
                        id_part = parts[1].split("/")[0]
                        content_ids.append(id_part)
            
            print(f"📊 IDs iniciales: {content_ids}")
            
            max_pages = 20
            for page in range(1, max_pages + 1):
                try:
                    data = {
                        "action": "Lastest",
                        "ContentsExist": content_ids,
                        "quantity": 10,
                        "section": 91
                    }
                    
                    print(f"📤 Solicitando página {page} con {len(content_ids)} IDs existentes")
                    
                    response = requests.post(self.ajax_endpoint, json=data, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    json_data = response.json()
                    
                    if 'contenidos' in json_data and json_data['contenidos']:
                        server_returned_ids = {str(cid) for cid in json_data['contenidos'] if cid != 0}
                        
                        nuevos_ids_a_procesar = server_returned_ids - set(content_ids)

                        if not nuevos_ids_a_procesar:
                            print("📄 No se encontraron más artículos nuevos. Deteniendo.")
                            break
                        
                        print(f"📰 Encontrados {len(nuevos_ids_a_procesar)} nuevos artículos para procesar.")
                        
                        detener_por_fecha = False
                        for contenido_id in nuevos_ids_a_procesar:
                            # La API no devuelve la URL completa, hay que construirla
                            # Esto es frágil, si cambia la estructura de URL, se romperá
                            # Asumimos una estructura común para los artículos.
                            url_articulo = f"https://www.pregon.com.ar/nota/{contenido_id}/"

                            if url_articulo in urls_vistas:
                                continue
                            
                            contenido_articulo = self._extraer_contenido_articulo(url_articulo)
                            urls_vistas.add(url_articulo) # Añadir después de la extracción para obtener la URL final

                            if contenido_articulo:
                                titulo, contenido, fecha_articulo, contenido_crudo = contenido_articulo
                                
                                # Verificar fecha límite
                                if self.fecha_limite and fecha_articulo and fecha_articulo.date() < self.fecha_limite:
                                    print(f"📅 Artículo muy antiguo ({fecha_articulo.date()}), deteniendo")
                                    detener_por_fecha = True
                                    break
                                
                                noticia_data = {
                                    "titulo": titulo,
                                    "contenido": contenido,
                                    "url": url_articulo,
                                    "fecha": fecha_articulo,
                                    "contenido_crudo": contenido_crudo,
                                    "media_name": self.media_name
                                }

                                if self._guardar_noticia(db, noticia_data):
                                    noticias_adicionales += 1

                            time.sleep(1)

                        if detener_por_fecha:
                            print("🛑 Deteniendo scraping por fecha límite.")
                            return noticias_adicionales

                        # Actualizar la lista de IDs para la siguiente petición
                        content_ids.extend(list(nuevos_ids_a_procesar))
                    else:
                        print("📄 No se encontraron 'contenidos' en la respuesta.")
                        break
                        
                except Exception as e:
                    print(f"❌ Error en página {page}: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error cargando artículos 'Ver Más': {e}")
        
        return noticias_adicionales 