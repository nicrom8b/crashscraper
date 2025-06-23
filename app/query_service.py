from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_, func
from app.db import Noticia
from app.llm_client import llm_client
import re
import logging

class QueryService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca noticias en la base de datos basándose en una consulta
        """
        # Limpiar y preparar la consulta
        search_terms = self._extract_search_terms(query)
        
        # Construir la consulta SQL
        db_query = self.db.query(Noticia)
        
        if search_terms:
            # Buscar en título y contenido
            conditions = []
            for term in search_terms:
                conditions.append(
                    or_(
                        Noticia.titulo.ilike(f"%{term}%"),
                        Noticia.contenido.ilike(f"%{term}%")
                    )
                )
            
            if conditions:
                db_query = db_query.filter(or_(*conditions))
        
        # Filtrar por accidentes de tránsito si la consulta lo sugiere
        if self._is_traffic_accident_query(query):
            db_query = db_query.filter(Noticia.es_accidente_transito == True)
        
        # Ordenar por fecha descendente
        db_query = db_query.order_by(Noticia.fecha.desc())
        
        # Limitar resultados
        news = db_query.limit(limit).all()
        
        # Convertir a diccionarios
        return [
            {
                "id": noticia.id,
                "titulo": noticia.titulo,
                "contenido": noticia.contenido[:200] + "..." if len(noticia.contenido) > 200 else noticia.contenido,
                "fecha": noticia.fecha.isoformat(),
                "url": noticia.url,
                "media_id": noticia.media_id,
                "es_accidente_transito": noticia.es_accidente_transito
            }
            for noticia in news
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la base de datos
        """
        total_news = self.db.query(Noticia).count()
        traffic_accidents = self.db.query(Noticia).filter(Noticia.es_accidente_transito == True).count()
        non_traffic_accidents = self.db.query(Noticia).filter(Noticia.es_accidente_transito == False).count()
        unclassified = self.db.query(Noticia).filter(Noticia.es_accidente_transito.is_(None)).count()
        
        # Estadísticas por medio de comunicación
        media_stats = {}
        media_counts = self.db.query(Noticia.media_id, func.count(Noticia.id)).group_by(Noticia.media_id).all()
        for media_id, count in media_counts:
            media_stats[media_id or "sin_medio"] = count
        
        return {
            "total_noticias": total_news,
            "accidentes_transito": traffic_accidents,
            "no_accidentes_transito": non_traffic_accidents,
            "sin_clasificar": unclassified,
            "por_medio": media_stats
        }
    
    def query_with_llm(self, question: str) -> Dict[str, Any]:
        """
        Procesa una pregunta usando el LLM y la base de datos
        """
        # Verificar si Ollama está disponible
        if not llm_client.is_available():
            return {
                "error": "Ollama no está disponible. Asegúrate de que esté corriendo.",
                "sugerencia": "Ejecuta: docker-compose up -d ollama"
            }
        
        # Buscar noticias relevantes
        logging.info(f"Buscando noticias relevantes para: '{question}'")
        relevant_news = self.search_news(question, limit=5)
        logging.info(f"Encontradas {len(relevant_news)} noticias relevantes.")
        
        # Construir el prompt para el LLM
        prompt = self._build_llm_prompt(question, relevant_news)
        logging.info(f"Prompt para el LLM:\n{prompt}")
        
        # Obtener respuesta del LLM
        logging.info("Enviando prompt al LLM...")
        llm_response = llm_client.query(prompt)
        logging.info(f"Respuesta del LLM: {llm_response}")
        
        return {
            "pregunta": question,
            "respuesta": llm_response,
            "noticias_relevantes": relevant_news,
            "total_noticias_encontradas": len(relevant_news)
        }
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """
        Extrae términos de búsqueda relevantes de la consulta
        """
        # Palabras clave relacionadas con accidentes de tránsito
        traffic_keywords = [
            'accidente', 'choque', 'colisión', 'siniestro', 'tránsito', 'vehículo',
            'auto', 'camión', 'moto', 'bicicleta', 'heridos', 'fallecidos',
            'ruta', 'autopista', 'calle', 'avenida', 'embestió', 'atropelló'
        ]
        
        # Palabras clave relacionadas con ubicaciones
        location_keywords = [
            'jujuy', 'salta', 'argentina', 'provincia', 'ciudad', 'barrio',
            'ruta 9', 'ruta 34', 'autopista', 'centro', 'norte', 'sur'
        ]
        
        # Extraer palabras relevantes
        words = re.findall(r'\b\w+\b', query.lower())
        relevant_terms = []
        
        for word in words:
            if (word in traffic_keywords or 
                word in location_keywords or 
                len(word) > 3):  # Palabras largas suelen ser más específicas
                relevant_terms.append(word)
        
        return relevant_terms[:5]  # Limitar a 5 términos más relevantes
    
    def _is_traffic_accident_query(self, query: str) -> bool:
        """
        Determina si la consulta está relacionada con accidentes de tránsito
        """
        traffic_indicators = [
            'accidente', 'choque', 'colisión', 'siniestro', 'tránsito', 'vehículo',
            'auto', 'camión', 'moto', 'bicicleta', 'heridos', 'fallecidos',
            'ruta', 'autopista', 'embestió', 'atropelló'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in traffic_indicators)
    
    def _build_llm_prompt(self, question: str, news: List[Dict[str, Any]]) -> str:
        """
        Construye el prompt para el LLM basándose en la pregunta y las noticias
        """
        if not news:
            return f"""
            Pregunta: {question}
            
            No se encontraron noticias relevantes en la base de datos.
            
            Por favor, responde de manera informativa indicando que no hay información disponible sobre este tema en la base de datos actual.
            """
        
        # Construir contexto con las noticias
        context = "\n\n".join([
            f"Noticia {i+1}:\nTítulo: {n['titulo']}\nContenido: {n['contenido']}\nFecha: {n['fecha']}\nMedio: {n['media_id']}"
            for i, n in enumerate(news)
        ])
        
        prompt = f"""
        Eres un asistente especializado en análisis de noticias sobre accidentes de tránsito en Argentina.
        
        Pregunta del usuario: {question}
        
        Contexto - Noticias relevantes de la base de datos:
        {context}
        
        Instrucciones:
        1. Analiza la pregunta del usuario
        2. Utiliza la información de las noticias proporcionadas para responder
        3. Si la pregunta no puede responderse con las noticias disponibles, indícalo claramente
        4. Proporciona una respuesta clara, concisa y útil
        5. Si hay estadísticas relevantes, inclúyelas
        6. Responde en español
        
        Respuesta:
        """
        
        return prompt 