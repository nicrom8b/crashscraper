import datetime
from .clarin import ClarinScraper
from .eltribuno import ElTribunoScraper
from .todojujuy import TodoJujuyScraper
from .somosjujuy import SomosJujuyScraper
from .jujuyalmomento import JujuyAlMomentoScraper
from .jujuydice import JujuyDiceScraper
from .pregon import PregonScraper

FECHA_LIMITE_GLOBAL = datetime.date(2025, 5, 15)
FECHA_LIMITE_TEST = datetime.date(2025, 6, 1)

SCRAPERS = [
    ClarinScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    ElTribunoScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    TodoJujuyScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    SomosJujuyScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    JujuyAlMomentoScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    JujuyDiceScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    PregonScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    # Agrega aquí los demás scrapers
] 