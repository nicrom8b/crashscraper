import ollama
import os
import logging

class LLMClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LLMClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Evitar reinicializar si la instancia ya existe
        if hasattr(self, 'client'):
            return
            
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Iniciando LLMClient con base_url: {self.base_url}")

        try:
            self.client = ollama.Client(host=self.base_url, timeout=300)
            self._is_available = self._check_availability()
            if self._is_available:
                logging.info(f"Conexión con Ollama en {self.base_url} exitosa.")
            else:
                logging.warning(f"No se pudo conectar con Ollama en {self.base_url}.")
        except Exception as e:
            logging.error(f"Error al inicializar el cliente de Ollama: {e}", exc_info=True)
            self.client = None
            self._is_available = False

    def _check_availability(self):
        if not self.client:
            return False
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def is_available(self):
        return self._is_available

    def get_version(self):
        if not self.is_available():
            return None
        try:
            return self.client.version().get('version', 'unknown')
        except Exception:
            return 'unknown'

    def get_available_models(self):
        if not self.is_available():
            return []
        try:
            models_info = self.client.list()
            return [model['name'] for model in models_info.get('models', [])]
        except Exception:
            return []

    def query(self, prompt: str, model: str = None) -> str:
        if not self.is_available():
            return "Error: El cliente LLM no está disponible o no se pudo conectar con Ollama."
        
        target_model = model or self.model
        
        try:
            logging.info(f"Enviando consulta al modelo {target_model}...")
            response = self.client.chat(
                model=target_model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.1}
            )
            logging.info("Respuesta recibida del LLM.")
            return response['message']['content']
        except Exception as e:
            logging.error(f"Error durante la consulta al LLM: {e}", exc_info=True)
            return f"Error al procesar la solicitud con el modelo {target_model}: {e}"

# Instancia Singleton
llm_client = LLMClient()