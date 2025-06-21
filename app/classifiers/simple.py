from . import SEARCH_TERMS, DEFAULT_THRESHOLDS

def es_accidente_simple(titulo: str, contenido: str, search_terms=None, threshold=None) -> bool:
    if search_terms is None:
        search_terms = SEARCH_TERMS
    if threshold is None:
        threshold = DEFAULT_THRESHOLDS['simple']
    
    texto = f"{titulo} {contenido}".lower()
    found_terms = sum(1 for term in search_terms if term in texto)
    return found_terms >= threshold 