# Validation — Fase 4: Agente LangGraph con streaming

## Criterios de aceptación

### Instalación y dependencias
- [x] `langgraph` aparece en `pyproject.toml` tras `uv add langgraph`
- [x] `uv run python -c "import langgraph"` no lanza errores

### Herramientas del agente (`backend/agent_tools.py`)
- [x] `analyze_image_tool` es un `@tool` de LangGraph que acepta imagen en base64
      y devuelve la lista de ingredientes como string
- [x] `search_recipes_tool` es un `@tool` de LangGraph que acepta una lista de
      ingredientes y devuelve resultados de búsqueda como string
- [x] Ambas tools tienen docstrings claros (el agente los usa para decidir cuándo invocarlas)

### Agente (`backend/agent.py`)
- [x] El grafo se construye con `create_react_agent` y las dos tools
- [x] El system prompt instruye al agente a responder en español si no hay texto
      del usuario, y en el idioma del texto si lo hay
- [x] El system prompt pide estructurar la receta con Markdown (h2, h3, listas)
- [x] `ChatQwen` se instancia con `enable_thinking=True` y `thinking_budget=200`
- [x] Se usa `thread_id="default"` como stub sin `MemorySaver`

### Filtrado de tokens de razonamiento
- [x] `strip_thinking_tokens("<think>razonamiento</think> texto visible")` 
      devuelve `" texto visible"` (sin el bloque think)
- [x] `strip_thinking_tokens("texto sin think")` devuelve `"texto sin think"` 
      sin modificaciones
- [x] Bloques `<think>` anidados o incompletos no rompen la función

### Endpoint `POST /chat`
- [x] Existe en `backend/main.py` y devuelve `StreamingResponse` con
      `media_type="text/event-stream"`
- [x] Acepta `multipart/form-data` con campos `image`, `message` y `session_id`
- [x] Rechaza imágenes con formato no soportado con status `422` y mensaje claro,
      antes de iniciar el stream
- [x] El stream emite al menos un evento `event: status` con el mensaje
      `"Analizando tu refrigerador…"` para cada petición
- [x] El stream emite al menos un evento `event: status` con el mensaje
      `"Buscando recetas en internet…"` para cada petición
- [x] El stream emite al menos un evento `event: token` con texto de la receta
- [x] El stream termina con un evento `event: done`
- [x] Los tokens `<think>...</think>` nunca aparecen en los eventos `token`
      enviados al cliente
- [x] El endpoint responde correctamente cuando `message` está vacío (primera consulta)

### Tests
- [x] `tests/test_agent.py` (o equivalente) incluye test unitario de
      `strip_thinking_tokens` con al menos 3 casos
- [x] Test de integración de `/chat` con una imagen JPEG real:
      el stream contiene eventos `status` y `token`
- [x] `uv run pytest` pasa sin errores

### Verificación manual
- [ ] Con `curl` o Postman: enviar una foto de refrigerador a `POST /chat`
      y ver el stream en la terminal mostrando eventos de status y tokens de texto
- [ ] La receta resultante está en Markdown válido (h2, h3, listas)
- [ ] La receta aparece en español cuando no se envía texto en `message`
- [ ] El servidor sigue levantando con 
      `uv run uvicorn backend.main:app --port 8005` sin errores de importación
