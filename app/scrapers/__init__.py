import datetime
from .eltribuno import ElTribunoScraper
from .eltribuno_salta import ElTribunoSaltaScraper
from .informate_salta import InformateSaltaScraper
from .todojujuy import TodoJujuyScraper
from .somosjujuy import SomosJujuyScraper
from .jujuyalmomento import JujuyAlMomentoScraper
from .jujuydice import JujuyDiceScraper
from .pregon import PregonScraper
from .elsubmarinojujuy import ElSubmarinoJujuyScraper
from .quepasasalta import QuePasaSaltaScraper

FECHA_LIMITE_GLOBAL = datetime.date(2025, 5, 15)
FECHA_LIMITE_TEST = datetime.date(2025, 6, 1)

SCRAPERS = [
    ElTribunoScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    ElTribunoSaltaScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    InformateSaltaScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    TodoJujuyScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    SomosJujuyScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    JujuyAlMomentoScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    JujuyDiceScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    PregonScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    ElSubmarinoJujuyScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    QuePasaSaltaScraper(fecha_limite=FECHA_LIMITE_GLOBAL),
    # Agrega aquí los demás scrapers
] 