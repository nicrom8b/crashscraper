import datetime
from .clarin import ClarinScraper
from .eltribuno import ElTribunoScraper

FECHA_LIMITE_GLOBAL = datetime.date(2025, 5, 15)

SCRAPERS = [
    ClarinScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    ElTribunoScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    # Agrega aquí los demás scrapers
] 