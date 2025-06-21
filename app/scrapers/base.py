from typing import List, Dict

class BaseScraper:
    def __init__(self, fecha_limite=None):
        self.fecha_limite = fecha_limite
    def scrape(self, db) -> int:
        """Método que debe implementar cada scraper. Debe guardar noticias usando la sesión db y devolver la cantidad guardada."""
        raise NotImplementedError 