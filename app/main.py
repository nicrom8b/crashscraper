from fastapi import FastAPI, Query
from app.db import SessionLocal, Noticia
from typing import Optional

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Crashscraper API"}

@app.get("/consultar")
def consultar(pregunta: str = Query(..., description="Pregunta en lenguaje natural")):
    # Aquí se integrará el LLM y la consulta a la base
    return {"respuesta": "Funcionalidad en desarrollo", "pregunta": pregunta} 