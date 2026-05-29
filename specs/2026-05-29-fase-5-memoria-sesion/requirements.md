# Requirements — Fase 5: Memoria de sesión

## Objetivo

Permitir que el agente Photo-Chef mantenga el contexto de la conversación entre
peticiones del mismo usuario durante la misma sesión de navegador. El usuario
puede hacer preguntas de seguimiento sobre la receta que recibió sin tener que
reenviar la foto.

## Alcance

### Dentro del alcance

- Integrar `MemorySaver` de LangGraph como checkpointer del agente
- Compartir una única instancia de `MemorySaver` (módulo-level singleton) entre
  todas las peticiones del mismo proceso de servidor
- Hacer la imagen opcional en el endpoint `/chat` (POST `multipart/form-data`)
- Identificar sesiones por `session_id` (string UUID generado por el frontend)
- El historial de conversación persiste **solo en RAM**; se pierde al reiniciar
  el servidor o al cerrar/recargar la pestaña del navegador (comportamiento by design)
- Actualizar el system prompt para que el agente responda preguntas de seguimiento
  sin re-invocar herramientas ya usadas
- Añadir pruebas de seguimiento en `tests/test_agent.py`

### Fuera del alcance

- Persistencia a disco o base de datos
- Autenticación o autorización de sesiones
- Límite de tiempo de expiración de sesiones
- Múltiples imágenes por sesión
- Generación del `session_id` en el backend (lo genera el frontend, Fase 6)

## Decisiones de diseño

### session_id

- Generado por el frontend como UUID v4 al cargar la página (en Fase 6)
- Enviado como campo de formulario (`session_id`) en cada POST a `/chat`
- Si el backend recibe `session_id` vacío o ausente, usa `"default"` como fallback
  (comportamiento actual, compatible con pruebas)

### MemorySaver singleton

- Instancia única `_memory = MemorySaver()` a nivel de módulo en `backend/agent.py`
- `build_agent` recibe la instancia como argumento o la importa del módulo
- El agente se reconstruye (compila) en cada petición, pero el estado del thread
  persiste entre compilaciones porque `MemorySaver` es el mismo objeto

### Imagen opcional

- Primera petición: `image` presente → se crea herramienta real `analyze_image_tool`
- Peticiones de seguimiento: `image` ausente → se crea herramienta stub que devuelve
  un mensaje explicativo en lugar de llamar al modelo de visión
- La herramienta stub tiene el mismo nombre (`analyze_image_tool`) para mantener
  coherencia con el historial del agente

### System prompt

- Se añade un párrafo de instrucción para seguimientos: el agente no debe volver
  a llamar herramientas si el historial ya contiene una receta completa, salvo que
  el usuario pida explícitamente una nueva

## Referencia al tech stack

- Orquestador: LangGraph `create_react_agent` con `checkpointer=MemorySaver()`
- Memoria: `from langgraph.checkpoint.memory import MemorySaver` (ya instalado con `langgraph`)
- Backend: FastAPI, imagen como `UploadFile | None`
- Sin cambios en modelos LLM ni en herramienta Tavily

## Contexto de la misión

La Fase 5 habilita el paso 5 del flujo principal de Photo-Chef:
"El usuario puede hacer preguntas de seguimiento sobre la receta y el agente
responde usando el contexto ya establecido."
