from . import SEARCH_TERMS, DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS
from . import contiene_exclusion

def es_accidente_ml_weighted(titulo: str, contenido: str, search_terms=None, weights=None, threshold=None) -> bool:
    if search_terms is None:
        search_terms = SEARCH_TERMS
    if weights is None:
        weights = DEFAULT_WEIGHTS
    if threshold is None:
        threshold = DEFAULT_THRESHOLDS['ml_weighted']
    
    texto = f"{titulo} {contenido}".lower()
    if contiene_exclusion(texto):
        return False
    score = sum(weights[term] for term in search_terms if term in texto)
    return score >= threshold 