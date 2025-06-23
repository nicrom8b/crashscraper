import requests
import json
import os
from typing import Dict, Any, List
import logging

class OllamaClient:
    def __init__(self):
        # Priorizar OLLAMA_BASE_URL si está disponible
        ollama_base_url = os.getenv('OLLAMA_BASE_URL')
        if ollama_base_url:
            self.base_url = ollama_base_url.rstrip('/')
        else:
            self.base_url = f"http://{os.getenv('OLLAMA_HOST', 'localhost')}:{os.getenv('OLLAMA_PORT', '11434')}"
        
        self.model = "mistral"  # Modelo por defecto
    
    def query(self, prompt: str, model: str = None) -> str:
        """
        Realiza una consulta al modelo LLM a través de Ollama usando la API moderna
        """
        if model is None:
            model = self.model
        
        # Intentar primero con /api/chat (API moderna)
        response = self._try_chat_api(prompt, model)
        if response:
            return response
        
        # Fallback a /api/generate (API legacy)
        return self._try_generate_api(prompt, model)
    
    def _try_chat_api(self, prompt: str, model: str) -> str:
        """Intenta usar la API de chat moderna"""
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            
            logging.info("Enviando petición a Ollama /api/chat...")
            response = requests.post(url, json=payload, timeout=90)  # Timeout de 90 segundos
            response.raise_for_status()
            result = response.json()
            logging.info("Respuesta recibida de Ollama /api/chat.")
            
            if 'message' in result and 'content' in result['message']:
                return result['message']['content']
            return result.get('response', '')
            
        except requests.exceptions.RequestException:
            return None  # Indica que este endpoint no está disponible
        except Exception:
            return None
    
    def _try_generate_api(self, prompt: str, model: str) -> str:
        """Usa la API de generate legacy como fallback"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            logging.info("Enviando petición a Ollama /api/generate...")
            response = requests.post(url, json=payload, timeout=90) # Timeout de 90 segundos
            response.raise_for_status()
            result = response.json()
            logging.info("Respuesta recibida de Ollama /api/generate.")
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            print(f"Error comunicándose con Ollama: {e}")
            return f"Error: No se pudo conectar con el modelo LLM. {str(e)}"
        except Exception as e:
            print(f"Error inesperado: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """
        Verifica si Ollama está disponible
        """
        logging.info("Verificando disponibilidad de Ollama...")
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logging.info("Ollama está disponible.")
                return True
            else:
                logging.warning(f"Ollama respondió con estado {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Error al verificar Ollama: {e}", exc_info=True)
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Obtiene la lista de modelos disponibles
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except:
            return []
    
    def get_version(self) -> str:
        """
        Obtiene la versión de Ollama
        """
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            if response.status_code == 200:
                return response.json().get('version', 'unknown')
            return 'unknown'
        except:
            return 'unknown'

# Instancia global del cliente
llm_client = OllamaClient() 