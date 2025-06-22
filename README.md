# crashscraper

Proyecto de scraping y consulta de noticias sobre accidentes de tránsito usando FastAPI, MariaDB y un LLM local (Mistral vía Ollama).

## Requisitos
- Docker y docker-compose
- pipenv (para desarrollo local)
- Python 3.11
- beautifulsoup4 (se instala automáticamente con pipenv)

## Estructura del proyecto
- `app/`: Lógica principal de la API, modelos, scrapers y clasificación.
- `scripts/`: Scripts utilitarios para inicializar, consultar y limpiar la base de datos.
- `docker-compose.yml`: Orquestación de servicios (API, DB, Ollama).
- `Dockerfile`: Imagen de la app para producción/desarrollo.

## Servicios
- **API**: http://localhost:8000
- **MariaDB**: localhost:3306
- **Ollama**: http://localhost:11434

## Variables de entorno
Se configuran en `docker-compose.yml` para la app:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `OLLAMA_HOST`, `OLLAMA_PORT`

## Fecha límite global para scraping
La fecha límite que usan todos los scrapers para filtrar noticias se define de forma global en:

```
app/scrapers/__init__.py
```

Busca la variable:

```python
FECHA_LIMITE_GLOBAL = datetime.date(2025, 1, 1)
```

Todos los scrapers reciben esta fecha como argumento al ser instanciados. Si quieres cambiar el rango de scraping, solo modifica este valor y se aplicará a todos los scrapers automáticamente.

## Flujo de scraping y clasificación
- Cada artículo extraído por los scrapers se guarda **inmediatamente** en la base de datos (commit tras cada inserción), con el campo `es_accidente_transito` en `NULL` (sin clasificar). Esto permite consultar la base de datos y ver los datos en tiempo real mientras el scraper está corriendo.
- Al finalizar el scraping, el runner recorre todas las noticias sin clasificar y les asigna el valor correcto (`True` o `False`) usando el clasificador automático.
- Esto permite manejar grandes volúmenes de datos y separar el scraping de la clasificación.

## Inicializar la base de datos con ejemplos

```bash
pipenv run python -m scripts.init_db
```
Esto crea la tabla y agrega ejemplos de noticias.

## Limpiar la base de datos (eliminar todas las noticias)

```bash
pipenv run python -m scripts.limpiar_db
```
Esto elimina todos los registros de la tabla `noticias` pero conserva la estructura.

## Consultar la base de datos por consola

```bash
pipenv run python -m scripts.consultar_db
```
Muestra todas las noticias ordenadas por fecha.

## Poblar la base de datos con noticias reales (scraping)

```bash
pipenv run python -m app.scraper_runner
```
Esto ejecuta todos los scrapers, guarda los artículos extraídos y luego los clasifica automáticamente.

## Levantar el proyecto completo (API + DB + Ollama)

```bash
docker-compose up --build
```

## Endpoints principales de la API
- `GET /`: Mensaje de bienvenida.
- `GET /consultar?pregunta=...`: (En desarrollo) Consulta en lenguaje natural usando LLM.

## Modelo de datos principal
Tabla `noticias`:
- `id`: int, PK
- `titulo`: str
- `contenido`: str
- `fecha`: date
- `url`: str
- `es_accidente_transito`: bool o NULL (sin clasificar)

## Scrapers disponibles
- `ElTribunoScraper`: Scrapea noticias de El Tribuno de Jujuy.
- `ClarinScraper`: Ejemplo dummy, reemplazar por scraping real.

## Clasificación automática
Las noticias se clasifican automáticamente como accidente de tránsito usando palabras clave, después de ser guardadas.

## Problemas comunes

### ModuleNotFoundError: No module named 'app'

Si ves este error al ejecutar scripts, asegúrate de correrlos como módulo usando el flag `-m` desde la raíz del proyecto:

```bash
pipenv run python -m scripts.init_db
pipenv run python -m app.scraper_runner
```

Esto permite que Python resuelva correctamente los imports de paquetes internos. 



# Diarios a Scrapear
1-  el tribuno jujuy: https://eltribunodejujuy.com/ # completed
2- todo jujuy: https://www.todojujuy.com/ # completed
3- somos jujuy: https://www.somosjujuy.com.ar/ # completed
4- jujuy al momento: https://www.jujuyalmomento.com/ # completed
5- jujuy dice: https://www.jujuydice.com.ar/ # completed Nota: Posiblemente no tenga noticias de accidentes
6- el pregon: https://www.pregon.com.ar/ # completed
7- el submarino: https://elsubmarinojujuy.com.ar/ # completed
8- eltribuno (Salta): https://www.eltribuno.com # completed
9- informate Salta: https://informatesalta.com.ar/ # completed
10: Que pasa salta: https://www.quepasasalta.com.ar # completed

