from typing import List, Dict, Any
from .classifiers.simple import es_accidente_simple
from .classifiers.stemmer import es_accidente_stemmer
from .classifiers.lemmatizer import es_accidente_lemmatizer
from .classifiers.ml_weighted import es_accidente_ml_weighted
from .classifiers import DEFAULT_THRESHOLDS

def es_accidente_transito(titulo: str, contenido: str, search_terms: List[str] = None) -> bool:
    if search_terms is None:
        search_terms = [
            'accidente', 'choque', 'colisión', 'siniestro vial',
            'accidente de tránsito', 'accidente vehicular', 'accidente automovilístico',
            'choque múltiple', 'choque frontal', 'volcamiento',
            'embestió', 'atropelló', 'atropellamiento',
            'vehículo', 'auto', 'camioneta', 'camión',
            'moto', 'motocicleta', 'bicicleta',
            'heridos', 'fallecidos', 'muertos', 'lesionados'
        ]
    texto = f"{titulo} {contenido}".lower()
    return any(term in texto for term in search_terms)

def determinar_accidente_transito(resultados_clasificadores: Dict[str, bool]) -> bool:
    """
    Determina si es accidente de tránsito basado en voto mayoritario de clasificadores.
    Retorna True si 2 o más clasificadores dan True.
    
    Args:
        resultados_clasificadores: Diccionario con los resultados de cada clasificador
            {'simple': bool, 'stemmer': bool, 'lemmatizer': bool, 'ml_weighted': bool}
    
    Returns:
        bool: True si es accidente de tránsito por voto mayoritario
    """
    votos_positivos = sum([
        resultados_clasificadores['simple'],
        resultados_clasificadores['stemmer'], 
        resultados_clasificadores['lemmatizer'],
        resultados_clasificadores['ml_weighted']
    ])
    
    return votos_positivos >= 2

def clasificar_noticia_completa(titulo: str, contenido: str, thresholds: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Clasifica una noticia usando todos los clasificadores disponibles y determina
    el resultado final por voto mayoritario.
    
    Args:
        titulo: Título de la noticia
        contenido: Contenido de la noticia
        thresholds: Diccionario con thresholds personalizados para cada clasificador
    
    Returns:
        Dict con los resultados de cada clasificador y el resultado final
    """
    # Usar thresholds por defecto si no se proporcionan
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    
    # Ejecutar todos los clasificadores
    resultado_simple = es_accidente_simple(titulo, contenido, threshold=thresholds['simple'])
    resultado_stem = es_accidente_stemmer(titulo, contenido, threshold=thresholds['stemmer'])
    resultado_lemma = es_accidente_lemmatizer(titulo, contenido, threshold=thresholds['lemmatizer'])
    resultado_ml = es_accidente_ml_weighted(titulo, contenido, threshold=thresholds['ml_weighted'])
    
    # Resultados individuales
    resultados_clasificadores = {
        'simple': resultado_simple,
        'stemmer': resultado_stem,
        'lemmatizer': resultado_lemma,
        'ml_weighted': resultado_ml
    }
    
    # Determinar resultado final por voto mayoritario
    es_accidente_final = determinar_accidente_transito(resultados_clasificadores)
    
    return {
        'resultados_individuales': resultados_clasificadores,
        'es_accidente_transito': es_accidente_final,
        'votos_positivos': sum(resultados_clasificadores.values()),
        'total_clasificadores': len(resultados_clasificadores)
    } 