# Roadmap

## ✅ Fase 0 — Andamiaje del proyecto
- Inicializar repositorio con `uv init`
- Crear virtualenv con `uv venv` y fijar versión de Python
- Configurar `.env` (keys de Qwen/Dashscope y Tavily)
- Definir estructura de carpetas: `backend/`, `frontend/`, `specs/`
- Crear `.gitignore` (excluir `.env`, `__pycache__`, `node_modules`, `dist/`, `.venv/`)

## ✅ Fase 1 — Esqueleto del backend
- Instalar dependencias base con `uv add`: FastAPI, uvicorn, python-dotenv
- Endpoint `GET /health` que confirma que el servidor corre en `localhost:8005`
- Configurar CORS para permitir el dev server de Svelte (`localhost:5173`)
- Servir la carpeta `frontend/dist/` como archivos estáticos desde FastAPI

## ✅ Fase 2 — Pipeline de visión
- Instalar `langchain-openai`, `openai` (el endpoint de Dashscope usa el protocolo OpenAI)
- Implementar función que recibe una imagen (base64) y devuelve la lista de ingredientes
  usando `qwen-vl-plus` vía `ChatOpenAI` apuntando al endpoint compatible de Dashscope
- Endpoint `POST /analyze-image` que recibe la foto y devuelve ingredientes
- Prueba manual con foto de refrigerador real
- Validar que la imagen sea JPEG, PNG o WEBP; rechazar otros formatos con error claro
- Si la identificación es incierta, el agente continúa e incluye advertencia
  al usuario sobre la baja confianza en los ingredientes detectados

## Fase 3 — Búsqueda de recetas
- Instalar `langchain-tavily` (`TavilySearchResults`)
- Implementar herramienta de búsqueda que toma la lista de ingredientes
  y devuelve resultados relevantes de recetas desde internet
- Prompt para que el agente seleccione y estructure la mejor receta del conjunto
- Configurar `qwen3.5-flash` con `enable_thinking=True` y `thinking_budget=200`
  para la síntesis de la receta

## Fase 4 — Agente LangGraph con streaming
- Instalar `langgraph`
- Construir agente ReAct con `create_react_agent`:
  - Herramienta 1: análisis de imagen (qwen-vl-plus)
  - Herramienta 2: búsqueda web (Tavily)
- El agente orquesta: foto → ingredientes → búsqueda → receta formateada
- Endpoint SSE que emite dos tipos de eventos:
  - `status`: mensajes de estado intermedio ("Analizando tu refrigerador…",
    "Buscando recetas en internet…", "Preparando tu receta…")
  - `token`: chunks de texto del LLM conforme llegan
- Implementado con `astream_events` de LangGraph, mapeando eventos internos
  del agente a los tipos de evento SSE
- El idioma de respuesta se determina en el system prompt según si el mensaje
  del usuario tiene texto o no

## Fase 5 — Memoria de sesión
- Integrar `MemorySaver` de LangGraph para mantener contexto en RAM
- Identificar sesiones por `session_id` (generado en el frontend al cargar la página)
- El agente recuerda la receta presentada para responder preguntas de seguimiento
- El historial se pierde al cerrar o recargar la pestaña (by design)

## Fase 6 — Frontend Svelte
- Inicializar proyecto Svelte 5 + Vite en `frontend/`
- Componente de carga de imagen: solo input tipo `file` (JPEG/PNG/WEBP),
  con preview antes de enviar; bloqueado una vez que inicia la conversación
- Componente de chat: burbuja de usuario + burbuja del agente con render
  progresivo (streaming via EventSource / SSE)
- Mensajes de estado intermedio visibles mientras el agente trabaja
  ("Analizando tu refrigerador…", "Buscando recetas…", "Preparando tu receta…")
- Renderizado de Markdown en las burbujas del agente usando `marked`
  (negritas, listas, cabeceras, emojis de la receta)
- Paleta visual: light mode, tonos cálidos (crema, naranja terracota `#E8622A`,
  verde salvia `#6B8F6B`), tipografía `Inter`, ancho máximo 720px
- Título y nombre del chatbot: "Photo-Chef"
- Indicador de escritura mientras llegan tokens
- `session_id` generado al cargar la página (UUID en memoria)
- Manejo de errores visible al usuario (imagen inválida, timeout, error del agente)

## Fase 7 — Integración y producción
- Script de build: `npm run build` en `frontend/` genera `frontend/dist/`
- FastAPI sirve `frontend/dist/` en la raíz `/`
- Verificar que toda la app corre con un solo comando: `uv run uvicorn backend.main:app --port 8005`
- Ajuste fino de prompts (idioma, tono, estructura Markdown de la receta)
- Verificar que el frontend renderiza correctamente el Markdown (negritas, listas, cabeceras)
- README con instrucciones de instalación y uso

## MVP listo
La app está terminada cuando un usuario puede:
1. Abrir el navegador, cargar una foto del refrigerador
2. Recibir una receta completa en ~30 segundos
3. Hacer al menos 3 preguntas de seguimiento sobre esa receta
   y recibir respuestas coherentes con el contexto
