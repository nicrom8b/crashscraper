import re
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from . import SEARCH_TERMS, DEFAULT_THRESHOLDS, contiene_exclusion

print("🔄 Cargando stopwords de NLTK...")
stops = set(stopwords.words("spanish"))
print("✅ Stopwords de NLTK cargadas exitosamente")

def es_accidente_stemmer(titulo: str, contenido: str, search_terms=None, threshold=None) -> bool:
    if search_terms is None:
        search_terms = SEARCH_TERMS
    if threshold is None:
        threshold = DEFAULT_THRESHOLDS['stemmer']
    
    stemmer = SnowballStemmer("spanish")
    texto = f"{titulo} {contenido}".lower()
    if contiene_exclusion(texto):
        return False
    tokens = re.findall(r'\w+', texto)
    tokens = [t for t in tokens if t not in stops]
    stems = [stemmer.stem(t) for t in tokens]
    search_stems = [stemmer.stem(term) for term in search_terms]
    found_terms = sum(1 for s in search_stems if s in stems)
    return found_terms >= threshold 