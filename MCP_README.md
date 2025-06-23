# 🚀 TO DO
## CrashScraper MCP Server

Servidor MCP (Model Context Protocol) para consultas de accidentes de tránsito en Argentina.

## 📋 Características

- **4 Herramientas disponibles** para consultar la base de datos
- **2 Recursos** con información general
- **Integración con LLM** para consultas en lenguaje natural
- **Compatible con Cursor, Cloude y otros clientes MCP**

## 🛠️ Herramientas Disponibles

### 1. `consultar_accidentes`
Consulta noticias usando lenguaje natural con LLM.

**Parámetros:**
- `pregunta` (string, requerido): Pregunta en lenguaje natural

**Ejemplo:**
```json
{
  "pregunta": "¿Qué tipos de accidentes son más comunes en Salta?"
}
```

### 2. `buscar_noticias`
Búsqueda específica en la base de datos.

**Parámetros:**
- `termino` (string, requerido): Término de búsqueda
- `limit` (integer, opcional): Número máximo de resultados (default: 10)
- `solo_accidentes` (boolean, opcional): Filtrar solo accidentes (default: false)

**Ejemplo:**
```json
{
  "termino": "choque",
  "limit": 5,
  "solo_accidentes": true
}
```

### 3. `obtener_estadisticas`
Obtiene estadísticas generales de la base de datos.

**Parámetros:** Ninguno

### 4. `obtener_noticia`
Obtiene una noticia específica por ID.

**Parámetros:**
- `id` (integer, requerido): ID de la noticia

**Ejemplo:**
```json
{
  "id": 3085
}
```

## 📊 Recursos Disponibles

### 1. `noticias_accidentes`
Base de datos de noticias sobre accidentes de tránsito en Argentina.

### 2. `estadisticas_generales`
Estadísticas generales de la base de datos de noticias.

## 🚀 Instalación y Uso

### 1. Instalar dependencias
```bash
pipenv install mcp
```

### 2. Ejecutar el servidor MCP
```bash
# Opción 1: Script directo
python scripts/run_mcp_server.py

# Opción 2: Con parámetros
python scripts/run_mcp_server.py --host 0.0.0.0 --port 8001 --debug

# Opción 3: Módulo Python
python -m app.mcp_server
```

### 3. Probar el servidor
```bash
python scripts/test_mcp_client.py
```

## 🔧 Configuración para Clientes MCP

### Cursor
1. Abrir configuración de Cursor
2. Buscar "MCP Servers"
3. Agregar la configuración del archivo `mcp_config.json`

### Cloude
1. Abrir configuración de Cloude
2. Buscar "MCP Servers"
3. Agregar la configuración del archivo `mcp_config.json`

### Otros clientes
Usar la configuración del archivo `mcp_config.json` como referencia.

## 📝 Ejemplos de Uso

### En Cursor/Cloude
```
Usuario: "Analiza los accidentes de tránsito en Salta usando crashscraper"

Cliente MCP automáticamente:
1. Se conecta al servidor crashscraper
2. Ejecuta: consultar_accidentes("accidentes en Salta")
3. Obtiene respuesta con análisis detallado
4. Lo incluye en el contexto del chat
```

### Consultas específicas
```
"Busca noticias sobre choques en Jujuy"
"¿Cuántos accidentes de tránsito hay en la base de datos?"
"Obtén estadísticas de accidentes por medio de comunicación"
"Muéstrame la noticia con ID 3085"
```

## 🔍 Monitoreo y Debug

### Logs del servidor
```bash
python scripts/run_mcp_server.py --debug
```

### Estado de la base de datos
```bash
python scripts/consultar_db.py "SELECT COUNT(*) FROM noticias WHERE es_accidente_transito = 1"
```

### Estado de Ollama
```bash
curl http://localhost:11434/api/tags
```

## 🐛 Solución de Problemas

### Error: "Connection refused"
- Verificar que el servidor MCP esté corriendo
- Verificar que el puerto esté disponible
- Verificar que Docker esté corriendo (para DB y Ollama)

### Error: "Database connection failed"
- Verificar que MariaDB esté corriendo: `docker-compose ps`
- Verificar credenciales en `mcp_config.json`

### Error: "Ollama not available"
- Verificar que Ollama esté corriendo: `docker-compose ps`
- Verificar que el modelo Mistral esté instalado

### Error: "MCP client not found"
- Verificar que la librería MCP esté instalada: `pipenv install mcp`
- Verificar que el cliente MCP esté configurado correctamente

## 📈 Estadísticas Actuales

- **Total noticias:** 724
- **Accidentes de tránsito:** 54
- **No accidentes:** 670
- **Fuentes:** 8 medios de comunicación

## 🔄 Actualización de Datos

Para actualizar la base de datos:

```bash
# Ejecutar scrapers
python scripts/scraper_runner.py

# Reclasificar noticias
python scripts/run_classifiers.py --force

# Reiniciar servidor MCP
# (detener y volver a ejecutar)
```

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs del servidor MCP
2. Verificar estado de servicios (DB, Ollama)
3. Ejecutar pruebas con `test_mcp_client.py`
4. Revisar configuración en `mcp_config.json` 
