# Plan — Fase 4: Agente LangGraph con streaming

## 1. Instalación de dependencias

- Instalar `langgraph` con `uv add langgraph`
- Confirmar que `langchain-qwq` ya está disponible (instalado en Fase 3)

## 2. Definición de las herramientas del agente

- Crear `backend/agent_tools.py`
- Envolver `analyze_image` de `vision.py` como tool de LangGraph (`@tool`)
  — recibe imagen en base64, devuelve lista de ingredientes como string
- Envolver la función de búsqueda de recetas de `search.py` como tool de LangGraph
  — recibe la lista de ingredientes, devuelve resultados formateados como string

## 3. Construcción del agente ReAct

- Crear `backend/agent.py`
- Instanciar `ChatQwen` con `qwen3.5-flash`, `enable_thinking=True`,
  `thinking_budget=200` y `streaming=True`
- Definir el system prompt:
  - El agente usa las dos herramientas en orden: imagen → búsqueda → receta
  - Responde en español si no hay texto del usuario; en el idioma del texto si lo hay
  - Estructura la receta con Markdown (h2, h3, listas, emojis)
- Construir el grafo con `create_react_agent(llm, tools=[analyze_image_tool, search_tool])`
- Usar `thread_id="default"` como stub (sin MemorySaver; la memoria real llega en Fase 5)

## 4. Filtrado de tokens de razonamiento

- Crear función auxiliar `strip_thinking_tokens(text: str) -> str` en `agent.py`
  que elimina bloques `<think>...</think>` del stream de texto antes de
  enviarlo al cliente

## 5. Endpoint SSE `POST /chat`

- Añadir el endpoint en `backend/main.py`
- Acepta `multipart/form-data` con los campos:
  - `image`: archivo de imagen (JPEG/PNG/WEBP)
  - `message`: texto opcional del usuario
  - `session_id`: string (stub; será usado en Fase 5)
- Devuelve `StreamingResponse` con `media_type="text/event-stream"`
- Emite los siguientes tipos de eventos SSE:
  - `status` — mensajes de estado intermedios mapeados desde eventos del agente:
    - `on_tool_start` con herramienta de visión → `"Analizando tu refrigerador…"`
    - `on_tool_start` con herramienta de búsqueda → `"Buscando recetas en internet…"`
    - `on_chain_start` del nodo de síntesis → `"Preparando tu receta…"`
  - `token` — chunks de texto del LLM tras filtrar bloques `<think>`
  - `done` — evento final vacío que indica fin del stream
- El endpoint reutiliza la validación de formato de imagen ya implementada

## 6. Tests

- Ampliar `tests/test_recipe.py` o crear `tests/test_agent.py`
- Test unitario de `strip_thinking_tokens`: verifica que elimina correctamente
  el bloque `<think>` y preserva el texto externo
- Test de integración del endpoint `/chat` con imagen real (JPEG):
  verifica que el stream emite al menos un evento `status` y al menos un evento `token`

## 7. Documentación y limpieza

- Actualizar `README.md` con el nuevo endpoint `/chat` y su contrato SSE
- Marcar la Fase 4 como completada en `specs/roadmap.md`
- Marcar todos los criterios en `specs/2026-05-29-fase-4-agente-langgraph-streaming/validation.md`
