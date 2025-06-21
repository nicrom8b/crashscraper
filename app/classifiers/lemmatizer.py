import spacy
import re
from . import SEARCH_TERMS, DEFAULT_THRESHOLDS

print("🔄 Cargando modelo de spaCy para español...")
nlp = spacy.load("es_core_news_sm")
print("✅ Modelo de spaCy cargado exitosamente")

def es_accidente_lemmatizer(titulo: str, contenido: str, search_terms=None, threshold=None) -> bool:
    if search_terms is None:
        search_terms = SEARCH_TERMS
    if threshold is None:
        threshold = DEFAULT_THRESHOLDS['lemmatizer']
    
    texto = f"{titulo} {contenido}".lower()
    doc = nlp(texto)
    lemmas = [token.lemma_ for token in doc if not token.is_stop]
    found_terms = sum(1 for term in search_terms if term in lemmas)
    return found_terms >= threshold 