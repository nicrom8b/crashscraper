from .base import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin
import time

class ElTribunoScraper(BaseScraper):
    BASE_URL = "https://eltribunodejujuy.com/seccion/policiales"

    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)

    def scrape(self, db) -> int:
        noticias_guardadas = 0
        pagina = 1
        seguir = True

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        while seguir:
            url_pagina = f"{self.BASE_URL}/{pagina}" if pagina > 1 else self.BASE_URL
            print(f"Scraping página {pagina}: {url_pagina}")
            
            try:
                response = requests.get(url_pagina, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Encuentra todos los artículos en la página
                items = soup.find_all('article') or soup.find_all(class_='article-item')
                
                if not items:
                    print(f"No se encontraron más artículos en la página {pagina}")
                    break

                found_articles = False
                
                for item in items:
                    try:
                        # Obtiene el enlace y título
                        link_element = item.find('a')
                        if not link_element:
                            continue
                            
                        url = urljoin(self.BASE_URL, link_element['href'])
                        
                        # Extrae la fecha del enlace
                        # Formato esperado: .../2025-1-29-0-31-0-titulo-de-la-noticia
                        date_parts = url.split('/')[-1].split('-')[:3]
                        if len(date_parts) < 3:
                            continue
                            
                        article_date = datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                        
                        # Si el artículo es anterior a la fecha límite, terminar
                        if self.fecha_limite and article_date < self.fecha_limite:
                            print(f"Se alcanzó la fecha límite ({self.fecha_limite}), finalizando búsqueda")
                            seguir = False
                            break
                        
                        found_articles = True
                        
                        # Obtiene el título
                        title_element = item.find('h2') or item.find('h3') or item.find(class_='title')
                        if not title_element:
                            continue
                            
                        titulo = title_element.text.strip()
                        
                        # Scrapea la página individual del artículo para más detalles
                        try:
                            print(f"Scrapeando artículo: {url}")
                            nota_resp = requests.get(url, headers=headers, timeout=10)
                            nota_resp.raise_for_status()
                            nota_soup = BeautifulSoup(nota_resp.text, "html.parser")
                            
                            # Intenta obtener el contenido del artículo
                            article = nota_soup.find('article')
                            if article:
                                paragraphs = article.find_all('p')
                                contenido_crudo = "\n".join([p.get_text() for p in paragraphs])
                            else:
                                contenido_crudo = ""
                            contenido = contenido_crudo.strip()
                            # Construir la fecha desde las partes extraídas de la URL
                            fecha = article_date
                            noticia = {
                                "titulo": titulo,
                                "contenido": contenido,
                                "contenido_crudo": contenido_crudo,
                                "fecha": fecha,
                                "url": url
                            }
                            # Guardar en la base de datos
                            from app.db import Noticia
                            noticia_obj = Noticia(
                                titulo=noticia["titulo"],
                                contenido=noticia["contenido"],
                                contenido_crudo=noticia["contenido_crudo"],
                                fecha=noticia["fecha"],
                                url=noticia["url"],
                                es_accidente_transito=None
                            )
                            db.add(noticia_obj)
                            db.commit()
                            noticias_guardadas += 1
                            print(f"Artículo extraído y guardado: {titulo}")
                            # Espera entre requests de artículos individuales
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f"Error scraping artículo individual {url}: {str(e)}")
                            continue
                    
                    except Exception as e:
                        print(f"Error procesando artículo: {str(e)}")
                        continue
                
                if not found_articles:
                    print(f"No se encontraron artículos válidos en la página {pagina}")
                
                pagina += 1
                time.sleep(3)  # Espera entre páginas
                
            except Exception as e:
                print(f"Error scraping El Tribuno: {e}")
                break
                
        return noticias_guardadas 