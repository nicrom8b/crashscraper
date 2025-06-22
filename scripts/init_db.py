#!/usr/bin/env python3
"""
Script para inicializar la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
from app.db import Base, engine, SessionLocal, Noticia

Base.metadata.create_all(bind=engine)

noticias_ejemplo = [
    Noticia(
        titulo="Accidente en la ruta 9: dos vehículos colisionaron",
        contenido="Un choque entre dos vehículos dejó varios heridos...",
        fecha=datetime.date(2024, 5, 10),
        url="https://ejemplo.com/accidente-ruta9",
        es_accidente_transito=True,
        media_id="ejemplo"
    ),
    Noticia(
        titulo="Robo en un comercio céntrico",
        contenido="Un local de ropa fue asaltado en la madrugada...",
        fecha=datetime.date(2024, 5, 12),
        url="https://ejemplo.com/robo-comercio",
        es_accidente_transito=False,
        media_id="ejemplo"
    ),
    Noticia(
        titulo="Choque múltiple en la autopista",
        contenido="Tres vehículos colisionaron en la autopista...",
        fecha=datetime.date(2024, 4, 28),
        url="https://ejemplo.com/choque-autopista",
        es_accidente_transito=True,
        media_id="ejemplo"
    ),
    Noticia(
        titulo="Inauguración de nuevo centro comercial",
        contenido="Se inauguró un nuevo centro comercial en la ciudad...",
        fecha=datetime.date(2024, 5, 2),
        url="https://ejemplo.com/inauguracion-cc",
        es_accidente_transito=False,
        media_id="ejemplo"
    ),
]

db = SessionLocal()
for noticia in noticias_ejemplo:
    db.add(noticia)
db.commit()
db.close() 