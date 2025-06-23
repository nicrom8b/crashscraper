# CrashScraper

CrashScraper es una aplicación web integral diseñada para recopilar, procesar, clasificar y consultar noticias sobre accidentes de tránsito en el norte de Argentina. Utiliza un conjunto de scrapers para extraer información de diversos diarios digitales, la almacena en una base de datos y la expone a través de una API RESTful y una interfaz web interactiva.

El proyecto integra un modelo de lenguaje grande (LLM) para permitir consultas en lenguaje natural sobre los datos recopilados.

**Tecnologías:** FastAPI, SQLAlchemy, MariaDB, Docker, Ollama, NLTK, spaCy.

## Características Principales

- **Scraping Multi-fuente**: Extrae noticias de 10 diarios digitales de Jujuy y Salta.
- **Procesamiento de Texto**: Limpia y normaliza el texto de las noticias para su análisis.
- **Clasificación Inteligente**: Utiliza un sistema de múltiples clasificadores (basados en keywords, stemming, lematización y ponderación) con un mecanismo de votación para determinar si una noticia trata sobre un accidente de tránsito.
- **API RESTful**: Provee endpoints para buscar, filtrar y obtener estadísticas de las noticias.
- **Interfaz Web Interactiva**: Un panel de control para visualizar estadísticas, una página de acciones para ejecutar scrapers/clasificadores y una interfaz de consulta.
- **Consultas con LLM**: Permite realizar preguntas en lenguaje natural (ej: "¿cuántos accidentes hubo en moto el fin de semana?") que son respondidas por un modelo de lenguaje grande (Mistral) a través de Ollama.
- **Orquestación con Docker**: Todo el ecosistema (API, base de datos, Ollama) se gestiona fácilmente con `docker-compose`.

## Arquitectura y Flujo de Datos

1.  **Ejecución de Scrapers**: El `Scraper Runner` (accesible desde la UI o por script) instancia y ejecuta todos los scrapers configurados.
2.  **Extracción y Almacenamiento**: Cada scraper navega por un sitio de noticias, extrae los artículos relevantes y los guarda en la base de datos MariaDB. El medio (diario) se gestiona en una tabla separada (`media`).
3.  **Clasificación**: El `Classifier Runner` (también ejecutable desde la UI o script) busca noticias sin clasificar en la base de datos.
4.  **Análisis y Votación**: Cada noticia es analizada por cuatro clasificadores distintos. El resultado final se decide por mayoría de votos.
5.  **Exposición vía API**: La API de FastAPI expone endpoints para acceder a los datos clasificados, obtener estadísticas y realizar búsquedas.
6.  **Interfaz de Usuario**: La UI, construida con HTML, CSS y JavaScript, consume la API para mostrar dashboards, permitir la ejecución de tareas y realizar consultas.
7.  **Consultas LLM**: Las preguntas en lenguaje natural se envían al `QueryService`, que interactúa con el `LLMClient` para obtener una respuesta del modelo Ollama.

## Puesta en Marcha

### Requisitos

- Docker y `docker-compose`
- `pipenv` (para desarrollo local)
- Python 3.11

### Usando Docker (Método Recomendado)

Este comando levantará todos los servicios necesarios: la API, la base de datos y el servidor Ollama con el modelo Mistral.

```bash
# Construye las imágenes y levanta los contenedores
docker-compose up --build
```
La primera vez, Docker descargará la imagen de MariaDB, Ollama y el modelo Mistral, lo cual puede tardar varios minutos.

### Desarrollo Local

Para desarrollo fuera de Docker, necesitarás una instancia local de MariaDB y Ollama.

```bash
# 1. Instalar dependencias
pipenv install

# 2. Configurar variables de entorno si es necesario
# (ej: en un archivo .env)

# 3. Ejecutar la aplicación
pipenv run uvicorn app.main:app --reload
```

## Servicios Expuestos

- **API / Interfaz Web**: [http://localhost:8000](http://localhost:8000)
- **MariaDB**: `localhost:3306`
- **Ollama API**: [http://localhost:11434](http://localhost:11434)

## Scrapers Implementados

El proyecto cuenta con scrapers para los siguientes medios:

| Medio                  | Clase del Scraper             | Archivo                         |
| ---------------------- | ----------------------------- | ------------------------------- |
| El Tribuno de Jujuy    | `ElTribunoScraper`            | `app/scrapers/eltribuno.py`     |
| Todo Jujuy             | `TodoJujuyScraper`            | `app/scrapers/todojujuy.py`     |
| Somos Jujuy            | `SomosJujuyScraper`           | `app/scrapers/somosjujuy.py`    |
| Jujuy Al Momento       | `JujuyAlMomentoScraper`       | `app/scrapers/jujuyalmomento.py`|
| Jujuy Dice             | `JujuyDiceScraper`            | `app/scrapers/jujuydice.py`     |
| El Pregón (Jujuy)      | `PregonScraper`               | `app/scrapers/pregon.py`        |
| El Submarino (Jujuy)   | `ElSubmarinoJujuyScraper`     | `app/scrapers/elsubmarinojujuy.py`|
| El Tribuno de Salta    | `ElTribunoSaltaScraper`       | `app/scrapers/eltribuno_salta.py`|
| Informate Salta        | `InformateSaltaScraper`       | `app/scrapers/informate_salta.py`|
| Qué Pasa Salta         | `QuePasaSaltaScraper`         | `app/scrapers/quepasasalta.py`  |


## Sistema de Clasificación

Para evitar falsos positivos, una noticia se clasifica como "accidente" solo si al menos dos de los siguientes clasificadores votan `True`:

- **`es_accidente_simple`**: Búsqueda simple de palabras clave.
- **`es_accidente_stemmer`**: Aplica stemming (raíz de palabras) a los términos de búsqueda para una coincidencia más amplia.
- **`es_accidente_lemmatizer`**: Usa lematización (lema de la palabra) con spaCy para una comprensión semántica más precisa.
- **`es_accidente_ml_weighted`**: Un modelo simple ponderado que asigna más peso a términos clave como "choque" o "siniestro vial".

## Scripts Utilitarios

Ubicados en el directorio `scripts/`. Deben ejecutarse como módulos desde la raíz del proyecto.

- **Inicializar la DB**: Crea las tablas y carga datos de ejemplo.
  ```bash
  pipenv run python -m scripts.init_db
  ```
- **Limpiar la DB**: Elimina todas las noticias, manteniendo las tablas.
  ```bash
  pipenv run python -m scripts.limpiar_db
  ```
- **Ejecutar Scrapers y Clasificadores**:
  ```bash
  pipenv run python -m app.scraper_runner
  ```

## Modelo de Datos

- **`media`**:
  - `id` (PK)
  - `name` (nombre del diario, ej: "todojujuy")
- **`noticias`**:
  - `id` (PK)
  - `titulo`, `contenido`, `fecha`, `url`
  - `media_id` (FK a `media.id`)
  - `contenido_crudo` (HTML original para re-procesamiento)
  - `classification` (Resultado final: 'ACCIDENTE' o 'NO_ACCIDENTE')
  - `es_accidente_transito` (Resultado final en formato booleano)
  - `es_accidente_simple` (Voto del clasificador de keywords)
  - `es_accidente_stem` (Voto del clasificador con stemming)
  - `es_accidente_lemma` (Voto del clasificador con lematización)
  - `es_accidente_ml` (Voto del clasificador ponderado)

## Configuración

### Variables de Entorno
Configuradas en `docker-compose.yml` para los contenedores.
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `OLLAMA_HOST`, `OLLAMA_PORT`

### Fecha Límite para Scraping
Para evitar scrapear noticias demasiado antiguas, se puede configurar una fecha límite global en `app/scrapers/__init__.py`, modificando la variable `FECHA_LIMITE_GLOBAL`.
```python
# app/scrapers/__init__.py
FECHA_LIMITE_GLOBAL = datetime.date(2025, 1, 1)
```
Esta fecha también se puede sobrescribir desde la interfaz web al ejecutar los scrapers.
