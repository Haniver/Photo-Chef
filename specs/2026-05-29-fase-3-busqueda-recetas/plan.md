# Plan — Fase 3: Búsqueda de recetas

## 1. Dependencias

- `uv add langchain-tavily` para instalar el wrapper de Tavily.
- Añadir `TAVILY_API_KEY` al `.env` y documentarlo en el `README`.
- Verificar que `langchain-qwq` ya está disponible (instalado en Fase 2).

## 2. Herramienta de búsqueda (`backend/search.py`)

- Función `search_recipes(ingredients: list[str]) -> list[dict]`.
- Construye una query a partir de los ingredientes (p. ej. `"recipes with tomato, eggs, cheese"`).
- Usa `TavilySearchResults(max_results=3)` para obtener 3 resultados de recetas.
- Devuelve la lista de resultados tal como los retorna Tavily
  (`url`, `content`, y opcionalmente `title`).

## 3. Síntesis de receta (`backend/recipe.py`)

- Función `synthesize_recipe(ingredients: list[str], search_results: list[dict]) -> str`.
- Instancia `ChatQwen` con:
  - `model="qwen3.5-flash"`
  - `enable_thinking=True`
  - `thinking_budget=200`
- System prompt que ordena al modelo:
  1. Leer los resultados de búsqueda.
  2. Seleccionar la receta más adecuada para los ingredientes disponibles.
  3. Presentarla en Markdown bien estructurado (título, ingredientes, pasos numerados).
  4. Usar el idioma del campo `language` que se le pasa (default: español).
- Devuelve el string Markdown generado por el modelo (sin el bloque de thinking).

## 4. Endpoint `POST /recipe`

- Añadir a `backend/main.py`.
- Request body:
  ```json
  {
    "ingredients": [
      { "name": "string", "confidence": 0.0 }
    ]
  }
  ```
- Lógica:
  1. Extraer los nombres de los ingredientes (incluye todos independientemente de confianza).
  2. Si hay ingredientes de baja confianza (`confidence < 0.5`), agregar advertencia al
     Markdown final: "⚠️ Algunos ingredientes se detectaron con baja confianza: …".
  3. Llamar a `search_recipes` → `synthesize_recipe`.
  4. Devolver `{"recipe": "<markdown>"}`.
- Errores manejados:
  - Lista vacía de ingredientes → HTTP 422 con mensaje claro.
  - Error de Tavily o del LLM → HTTP 502 con mensaje de error.

## 5. Tests automatizados (`tests/test_recipe.py`)

- Configurar `pytest` si no está ya instalado (`uv add --dev pytest pytest-asyncio`).
- Tests unitarios (mocks de Tavily y del LLM):
  - `test_search_recipes_builds_correct_query`: verifica que la query enviada a Tavily
    contiene los ingredientes.
  - `test_search_recipes_returns_results`: mock de Tavily devuelve 3 resultados;
    la función los retorna sin transformación.
  - `test_synthesize_recipe_calls_llm`: mock del LLM; verifica que el prompt incluye
    los ingredientes y los resultados de búsqueda.
  - `test_synthesize_recipe_returns_markdown_string`: mock del LLM retorna texto;
    la función devuelve ese string.
- Tests de integración del endpoint (con `httpx.AsyncClient` y mocks):
  - `test_recipe_endpoint_returns_200_with_ingredients`.
  - `test_recipe_endpoint_returns_422_with_empty_ingredients`.
  - `test_recipe_endpoint_warns_low_confidence_ingredients`.
