from .base import BaseScraper
from typing import List, Dict
import datetime

class ClarinScraper(BaseScraper):
    def __init__(self, fecha_limite=None):
        super().__init__(fecha_limite)
    def scrape(self, db) -> int:
        from app.db import Noticia
        noticia_obj = Noticia(
            titulo="Ejemplo de noticia de Clarín",
            contenido="Contenido de la noticia...",
            contenido_crudo="Contenido de la noticia asdasdasdasdasdasd...",
            fecha=datetime.date.today(),
            url="https://clarin.com/ejemplo",
            es_accidente_transito=None
        )
        db.add(noticia_obj)
        db.commit()
        print(f"Artículo extraído y guardado: Ejemplo de noticia de Clarín")
        return 1 