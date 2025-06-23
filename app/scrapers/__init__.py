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

FECHA_LIMITE_GLOBAL = datetime.date(2025, 6, 1)
FECHA_LIMITE_TEST = datetime.date(2025, 6, 1)

# Esta lista ahora contiene las CLASES, no las instancias.
SCRAPERS = [
    ElTribunoScraper,
    ElTribunoSaltaScraper,
    InformateSaltaScraper,
    TodoJujuyScraper,
    SomosJujuyScraper,
    JujuyAlMomentoScraper,
    JujuyDiceScraper,
    PregonScraper,
    ElSubmarinoJujuyScraper,
    QuePasaSaltaScraper,
] 