#!/usr/bin/env python3
"""
Script para inicializar la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import Base, engine

# Crear todas las tablas
Base.metadata.create_all(bind=engine)
print("✅ Base de datos inicializada correctamente") 