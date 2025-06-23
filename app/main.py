from fastapi import FastAPI, Query, Depends, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db import SessionLocal, Noticia, get_db
from app.query_service import QueryService, Consulta
from app.llm_client import llm_client
from typing import Optional, List, Dict, Any
import datetime
import logging
import asyncio
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(
    title="Crashscraper API",
    description="API para consulta de noticias sobre accidentes de tránsito usando LLM",
    version="1.0.0"
)

# Montar directorio estático
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar plantillas de Jinja2
templates = Jinja2Templates(directory="app/templates")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """Dependency para obtener la sesión de la base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page": "consulta"})

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "page": "dashboard"})

@app.get("/acciones")
def acciones(request: Request):
    return templates.TemplateResponse("acciones.html", {"request": request, "page": "acciones"})

@app.get("/estadisticas")
def get_stats(db: Session = Depends(get_db)):
    query_service = QueryService(db)
    return query_service.get_statistics()

@app.post("/consultar")
def consultar(
    consulta: Consulta, db: Session = Depends(get_db)
):
    try:
        query_service = QueryService(db)
        # Devolvemos directamente el objeto que genera el servicio
        return query_service.query_with_llm(consulta.pregunta)
    except Exception as e:
        logging.exception("Error en la consulta")
        raise HTTPException(status_code=500, detail=f"Error en la consulta: {str(e)}")

@app.get("/buscar")
def buscar_noticias(
    q: str = Query(..., description="Término de búsqueda"),
    limit: int = Query(10, description="Número máximo de resultados"),
    db: SessionLocal = Depends(get_db)
):
    """
    Búsqueda simple de noticias en la base de datos
    """
    try:
        query_service = QueryService(db)
        results = query_service.search_news(q, limit=limit)
        return {
            "termino_busqueda": q,
            "total_resultados": len(results),
            "noticias": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda: {str(e)}")

@app.get("/estadisticas")
def obtener_estadisticas(db: SessionLocal = Depends(get_db)):
    """
    Obtiene estadísticas de la base de datos
    """
    try:
        query_service = QueryService(db)
        stats = query_service.get_statistics()
        return {
            "fecha_consulta": datetime.datetime.now().isoformat(),
            "estadisticas": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@app.get("/ollama/status")
def ollama_status():
    """
    Verifica el estado de Ollama y modelos disponibles
    """
    try:
        is_available = llm_client.is_available()
        models = llm_client.get_available_models() if is_available else []
        version = llm_client.get_version() if is_available else 'unknown'
        
        return {
            "ollama_disponible": is_available,
            "version": version,
            "modelos_disponibles": models,
            "modelo_por_defecto": llm_client.model,
            "url": llm_client.base_url
        }
    except Exception as e:
        return {
            "ollama_disponible": False,
            "version": "unknown",
            "error": str(e),
            "url": llm_client.base_url
        }

@app.get("/noticias/{noticia_id}")
def obtener_noticia(noticia_id: int, db: SessionLocal = Depends(get_db)):
    """
    Obtiene una noticia específica por ID
    """
    try:
        noticia = db.query(Noticia).filter(Noticia.id == noticia_id).first()
        if not noticia:
            raise HTTPException(status_code=404, detail="Noticia no encontrada")
        
        return {
            "id": noticia.id,
            "titulo": noticia.titulo,
            "contenido": noticia.contenido,
            "fecha": noticia.fecha.isoformat(),
            "url": noticia.url,
            "media_id": noticia.media_id,
            "es_accidente_transito": noticia.es_accidente_transito
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo noticia: {str(e)}")

@app.get("/noticias")
def listar_noticias(
    limit: int = Query(20, description="Número máximo de resultados"),
    offset: int = Query(0, description="Número de resultados a saltar"),
    es_accidente: Optional[bool] = Query(None, description="Filtrar por accidentes de tránsito"),
    media_id: Optional[str] = Query(None, description="Filtrar por medio de comunicación"),
    db: SessionLocal = Depends(get_db)
):
    """
    Lista noticias con filtros opcionales
    """
    try:
        query = db.query(Noticia)
        
        # Aplicar filtros
        if es_accidente is not None:
            query = query.filter(Noticia.es_accidente_transito == es_accidente)
        
        if media_id:
            query = query.filter(Noticia.media_id == media_id)
        
        # Ordenar por fecha descendente
        query = query.order_by(Noticia.fecha.desc())
        
        # Aplicar paginación
        total = query.count()
        noticias = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "noticias": [
                {
                    "id": n.id,
                    "titulo": n.titulo,
                    "contenido": n.contenido[:200] + "..." if len(n.contenido) > 200 else n.contenido,
                    "fecha": n.fecha.isoformat(),
                    "url": n.url,
                    "media_id": n.media_id,
                    "es_accidente_transito": n.es_accidente_transito
                }
                for n in noticias
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando noticias: {str(e)}")

async def stream_script_output(command: list[str]):
    """
    Ejecuta un script en un subproceso y transmite su salida stdout y stderr.
    """
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def reader(stream, prefix):
        while True:
            line = await stream.readline()
            if not line:
                break
            log_line = f"{prefix}: {line.decode('utf-8')}"
            print(log_line, end="")
            yield log_line

    # Combinamos la salida estándar y la de error en un solo stream de logs
    async for log_line in reader(process.stdout, "INFO"):
        yield log_line
    async for log_line in reader(process.stderr, "ERROR"):
        yield log_line

    await process.wait()

@app.post("/acciones/ejecutar-scrapers")
async def ejecutar_scrapers(fecha_limite: Optional[str] = Query(None)):
    command = ["pipenv", "run", "python", "app/scraper_runner.py"]
    if fecha_limite:
        command.extend(["--fecha-limite", fecha_limite])
    return StreamingResponse(stream_script_output(command), media_type="text/plain")

@app.post("/acciones/ejecutar-clasificadores")
async def ejecutar_clasificadores():
    command = ["pipenv", "run", "python", "scripts/run_classifiers.py"]
    return StreamingResponse(stream_script_output(command), media_type="text/plain") 