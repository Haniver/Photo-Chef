# Validation — Fase 3: Búsqueda de recetas

## Criterios de aceptación

La fase está completa y lista para merge cuando **todos** los siguientes puntos son verdaderos.

---

### ✅ 1. Dependencias instaladas

```bash
uv run python -c "from langchain_tavily import TavilySearch; print('ok')"
# Debe imprimir: ok
```

- `pyproject.toml` lista `langchain-tavily` como dependencia.

---

### ✅ 2. Endpoint existe y el servidor arranca

```bash
uv run uvicorn backend.main:app --port 8005 --reload
```

- El servidor arranca sin errores.
- La ruta `POST /recipe` aparece en `http://localhost:8005/docs`.

---

### ✅ 3. Suite de tests pasa al completo

```bash
uv run pytest tests/test_recipe.py -v
```

- Todos los tests pasan (sin skip, sin error).
- Los tests no realizan llamadas reales a Tavily ni a Dashscope (usan mocks).
- Cobertura mínima: los 7 casos del plan (5 unitarios + 3 de integración) están presentes.

Casos obligatorios:

| Test | Verifica |
|---|---|
| ✅ `test_search_recipes_builds_correct_query` | La query a Tavily contiene los nombres de los ingredientes |
| ✅ `test_search_recipes_returns_results` | Con mock de 3 resultados, la función los retorna sin transformar |
| ✅ `test_synthesize_recipe_calls_llm` | El prompt al LLM incluye ingredientes y resultados de búsqueda |
| ✅ `test_synthesize_recipe_returns_markdown_string` | La función retorna el string del LLM directamente |
| ✅ `test_recipe_endpoint_returns_200_with_ingredients` | HTTP 200 con body `{"recipe": "..."}` |
| ✅ `test_recipe_endpoint_returns_422_with_empty_ingredients` | HTTP 422 cuando `ingredients` es lista vacía |
| ✅ `test_recipe_endpoint_warns_low_confidence_ingredients` | El Markdown resultante contiene advertencia ⚠️ cuando hay ingredientes con `confidence < 0.5` |

---

### ✅ 4. Respuesta del endpoint tiene el formato correcto

```bash
curl -s -X POST http://localhost:8005/recipe \
  -H "Content-Type: application/json" \
  -d '{"ingredients": [{"name": "tomate", "confidence": 0.9}, {"name": "huevo", "confidence": 0.8}]}' \
  | python3 -m json.tool
```

- Código HTTP: `200`.
- La respuesta tiene la forma:
  ```json
  { "recipe": "# Título de la receta\n\n..." }
  ```
- El string `recipe` contiene al menos un título Markdown (`#`) y una lista de pasos.

---

### ✅ 5. Advertencia de baja confianza se incluye correctamente

```bash
curl -s -X POST http://localhost:8005/recipe \
  -H "Content-Type: application/json" \
  -d '{"ingredients": [{"name": "tomate", "confidence": 0.9}, {"name": "algo_raro", "confidence": 0.3}]}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('ok' if '⚠️' in r['recipe'] else 'FAIL')"
# Debe imprimir: ok
```

---

### ✅ 6. Lista vacía de ingredientes devuelve error claro

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8005/recipe \
  -H "Content-Type: application/json" \
  -d '{"ingredients": []}'
# Debe imprimir: 422
```

---

### ✅ 7. Variables de entorno documentadas

- `.env.example` (o el `README`) incluye la línea `TAVILY_API_KEY=your_key_here`.
