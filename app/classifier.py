from typing import List

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