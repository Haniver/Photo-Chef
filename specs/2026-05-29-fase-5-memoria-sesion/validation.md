# Validation — Fase 5: Memoria de sesión

## Criterios de aceptación

### A. MemorySaver integrado

- [x] `backend/agent.py` importa `MemorySaver` y crea una instancia global `_memory`
- [x] `create_react_agent` recibe `checkpointer=_memory`
- [x] El agente compilado puede leer y escribir en el checkpointer por `thread_id`

### B. Imagen opcional en `/chat`

- [x] El endpoint `/chat` acepta peticiones sin imagen (campo `image` ausente o vacío)
- [x] Cuando `image` está ausente, no se lanza error de validación de formato
- [x] Cuando `image` está presente, la validación de formato funciona igual que antes

### C. Herramienta stub para seguimientos

- [x] Cuando `image` es None, se crea un stub `analyze_image_tool` que devuelve
  el mensaje "No se ha proporcionado imagen nueva. Usa el historial de conversación
  para responder." (o equivalente)
- [x] El stub no hace ninguna llamada a la API de Dashscope

### D. Contexto persistente entre peticiones

- [x] Enviando dos peticiones al mismo `thread_id`:
  1. Primera petición con imagen → el agente devuelve una receta
  2. Segunda petición con texto (sin imagen) → el agente responde usando el contexto
     de la receta anterior sin volver a llamar `analyze_image_tool` ni `search_recipes_tool`
- [x] Enviando peticiones a `thread_id` distintos: no hay contaminación de contexto

### E. Pruebas automatizadas

- [x] `tests/test_agent.py` tiene al menos un test de seguimiento que:
  - Simula una primera petición (mockeando herramientas)
  - Simula una segunda petición con la misma `thread_id` sin imagen
  - Verifica que el agente devuelve una respuesta coherente con el contexto previo
- [x] `uv run pytest tests/test_agent.py -v` pasa sin errores

### F. Prueba manual de regresión

- [x] `GET /health` sigue respondiendo `{"status": "ok"}`
- [ ] Una primera petición con imagen real sigue generando una receta completa con streaming SSE
- [ ] Una pregunta de seguimiento como "¿a qué temperatura va el horno?" recibe
  una respuesta coherente sin re-analizar la imagen

## Casos borde

- [x] `session_id` vacío → el backend usa `"default"` como thread_id sin errores
- [x] Dos sesiones paralelas con `session_id` distintos → no se mezcla su historial
- [x] Primera petición sin imagen → el agente responde indicando que necesita una foto
  (no crash; puede ser un mensaje de error amigable o simplemente usar la herramienta stub)
