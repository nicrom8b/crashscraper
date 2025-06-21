# Términos de búsqueda centralizados para clasificación de accidentes
SEARCH_TERMS = [
    'accidente', 'choque', 'colisión','colisionó', 'vial',
    'accidente de tránsito', 'accidente vehicular',
    'choque frontal', 'volcamiento', 'vehículo'
    'embestió', 'atropelló', 'siniestro', 'atropello'
    'heridos', 'fallecidos', 'muertos', 'lesionados', 'volcó'
]

# Pesos para el clasificador ML weighted
DEFAULT_WEIGHTS = {term: 1 for term in SEARCH_TERMS}
DEFAULT_WEIGHTS.update({
    'accidente': 2, 
    'siniestro vial': 2, 
    'choque': 2,
    'siniestro': 2,
    'colisión': 2,
    'colisionó': 2,
    'vial': 2,
    'volcó': 2
})

# Thresholds por defecto para cada clasificador
DEFAULT_THRESHOLDS = {
    'simple': 2,        # Al menos 1 término debe aparecer
    'stemmer': 2,       # Al menos 1 término debe aparecer después del stemming
    'lemmatizer': 2,    # Al menos 1 término debe aparecer después de lematización
    'ml_weighted': 2    # Score mínimo de 2 para clasificar como accidente
} 