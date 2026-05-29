# Requirements — Fase 4: Agente LangGraph con streaming

## Objetivo

Construir el agente ReAct con LangGraph que orquesta el flujo completo:
foto → ingredientes → búsqueda → receta. Exponerlo vía un endpoint SSE que
entregue el resultado en streaming token a token, con eventos de estado
intermedios para que el frontend pueda mostrar progreso.

## Contexto

Las Fases 2 y 3 ya implementan las funciones atómicas:
- `vision.py` — análisis de imagen con `qwen-vl-plus`
- `search.py` — búsqueda de recetas con Tavily
- `recipe.py` — síntesis de receta con `qwen3.5-flash`

Esta fase integra esas piezas en un agente LangGraph y expone el resultado
como un endpoint SSE, sustituyendo el uso directo de esas funciones en la API.

## Decisiones

| Decisión | Elección | Motivo |
|---|---|---|
| Endpoint SSE | `POST /chat` (nuevo, coexiste con `/analyze-image`) | Separación de responsabilidades; `/analyze-image` queda para pruebas aisladas |
| Integración de tools | Envolver directamente `vision.py` y `search.py` | Sin refactoring innecesario; las interfaces ya son correctas |
| Memoria de sesión | Stub: `thread_id="default"`, sin `MemorySaver` | La memoria real se implementa en Fase 5 |
| Tokens de razonamiento | Filtrar `<think>...</think>` antes de enviar al cliente | El usuario no necesita ver el razonamiento interno del modelo |
| Idioma de respuesta | Instrucción en system prompt: español si no hay texto, idioma del texto si lo hay | Comportamiento definido en la misión del producto |

## Contrato del endpoint `POST /chat`

**Request** — `multipart/form-data`:
- `image` (file, requerido): imagen JPEG, PNG o WEBP del refrigerador
- `message` (string, opcional): texto del usuario; vacío = primera consulta
- `session_id` (string, opcional): identificador de sesión (stub en esta fase)

**Response** — `text/event-stream` (SSE):

```
event: status
data: {"message": "Analizando tu refrigerador…"}

event: token
data: {"text": "## Tortilla de patatas\n"}

event: done
data: {}
```

**Errores** (antes de iniciar el stream):
- `422` — imagen faltante o formato no soportado (reutiliza validación de Fase 2)
- `500` — error interno del agente (devuelve JSON con `detail`)

## Fuera de alcance

- Memoria de sesión real (`MemorySaver`, `session_id` funcional) → Fase 5
- Frontend que consume este endpoint → Fase 6
- Ajuste fino de prompts ni estilo visual → Fase 7
- Soporte para más de una imagen por sesión (no está en la misión)
- Procesamiento de cantidades exactas de ingredientes (fuera de la misión)

## Restricciones técnicas

- El modelo `qwen3.5-flash` se accede vía `ChatQwen` de `langchain-qwq`
  con `DASHSCOPE_API_KEY` del `.env`
- `enable_thinking=True` con `thinking_budget=200` ya probado en Fase 3
- El streaming se implementa con `astream_events` de LangGraph
- Todos los eventos SSE siguen el formato estándar: `event: <type>\ndata: <json>\n\n`
- La app sigue corriendo con `uv run uvicorn backend.main:app --port 8005`
