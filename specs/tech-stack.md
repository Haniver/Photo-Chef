# Tech Stack

## Frontend

| Capa | Tecnología | Versión |
|---|---|---|
| Framework UI | Svelte | 5.x |
| Build tool | Vite | 6.x |
| Servidor de desarrollo | Vite dev server (solo en desarrollo) | — |
| Producción | Archivos estáticos servidos por FastAPI | — |

**Decisión clave:** el frontend se compila a HTML/CSS/JS puro (`frontend/dist/`).
No se necesita Node ni ningún servidor JavaScript en producción. FastAPI sirve
esos archivos estáticos directamente con `StaticFiles`.

## Backend

| Capa | Tecnología | Notas |
|---|---|---|
| Framework HTTP | FastAPI | Async, OpenAPI automático |
| Servidor ASGI | Uvicorn | Corre en `localhost:8005` con `uv run uvicorn` |
| Variables de entorno | python-dotenv | Lee el `.env` |

## Agente

| Capa | Tecnología | Notas |
|---|---|---|
| Orquestador de agente | LangGraph (`create_react_agent`) | Patrón ReAct moderno, soporta streaming |
| Memoria de sesión | `MemorySaver` (LangGraph) | Solo en RAM, por `session_id` |
| Integración LLM | `langchain-qwq` (`ChatQwen`) | Wrapper nativo para Dashscope |
| Herramienta de visión | `qwen-vl-plus` (multimodal) | Identifica ingredientes; una foto por sesión |
| Herramienta de búsqueda | Tavily (`TavilySearchResults`) | Busca recetas en internet |

### Flujo del agente

```
foto (base64)
    └─→ [Tool: qwen-vl-plus] → lista de ingredientes
                                    └─→ [Tool: Tavily] → resultados de recetas
                                                              └─→ LLM → receta formateada
                                                                             └─→ [seguimiento] → respuesta contextual
```

## LLM

| Modelo | Uso | Provider | Integración LangChain |
|---|---|---|---|
| `qwen-vl-plus` | Análisis de imagen → ingredientes | Alibaba Dashscope | `ChatQwen` de `langchain-qwq` |
| `qwen3.5-flash` | Síntesis de receta + conversación | Alibaba Dashscope | `ChatQwen` de `langchain-qwq` |

Ambos se acceden vía la misma clave (`DASHSCOPE_API_KEY` en `.env`).

### Razonamiento de `qwen3.5-flash`

El modelo se usa con `thinking_budget=200` (tokens de razonamiento interno).
Suficiente para tareas de síntesis y conversación sin incurrir en el coste
de un presupuesto de razonamiento alto.

## Idioma de respuesta

- Si el usuario solo envía una foto (sin texto): responde en **español**
- Si el usuario envía texto: responde en el **mismo idioma del texto**
- Implementado vía instrucción en el system prompt del agente

## Servidor y puertos

| Entorno | URL |
|---|---|
| Backend FastAPI (dev y prod) | `http://localhost:8005` |
| Frontend Vite dev server | `http://localhost:5173` |

El puerto `8005` fue seleccionado porque `8000` y `8001` ya están en uso
en la máquina de desarrollo.

## Diseño visual del frontend

- **Modo:** light mode únicamente
- **Paleta:** tonos cálidos de cocina — blancos cálidos, cremas, acentos en naranja
  terracota (`#E8622A`) y verde salvia (`#6B8F6B`); nada de degradados morados
- **Tipografía:** `Inter` para texto de UI; la receta se renderiza con buen
  espaciado y jerarquía visual clara (h2, h3, listas)
- **Layout:** columna centrada, ancho máximo ~720px; foto del fridge arriba,
  chat debajo; sensación de app de cocina, no de herramienta técnica
- **Nombre visible en la UI:** "Photo-Chef"

## Streaming

Las respuestas del agente se envían en streaming token a token. El backend expone
un endpoint de tipo Server-Sent Events (SSE) y el frontend renderiza cada chunk
conforme llega, replicando la experiencia de escritura progresiva de ChatGPT.

Además de los tokens de texto, el SSE emite **eventos de estado intermedio**
que el frontend muestra como mensajes de sistema mientras el agente trabaja:

| Evento | Mensaje visible en UI |
|---|---|
| Agente empieza a analizar la imagen | "Analizando tu refrigerador…" |
| Agente lanza búsqueda de recetas | "Buscando recetas en internet…" |
| Agente empieza a redactar respuesta | "Preparando tu receta…" |

Estos mensajes desaparecen en cuanto empieza el streaming del texto final.

## Formato de la receta

El agente devuelve la receta en Markdown estructurado. El system prompt instruye
al modelo a usar siempre este esquema:

```markdown
## 🍲 Nombre de la receta

**Tiempo:** ~XX minutos | **Porciones:** X

### Ingredientes
- Item 1
- Item 2

### Pasos
1. Primer paso.
2. Segundo paso.

### Consejo del chef
Texto opcional con tip o sustitución sugerida.
```

El frontend renderiza el Markdown (usando una librería ligera como `marked`) para
que se vea con formato visual (negritas, listas, cabeceras) en lugar de texto plano.
Las respuestas de seguimiento (preguntas sobre la receta) se muestran como texto
Markdown libre, sin estructura forzada.

## Identidad del chatbot

- **Nombre:** Photo-Chef
- Se presenta como "Photo-Chef" en las burbujas del chat y en el título de la app

## Restricciones de entrada

- **Una sola foto por conversación**: el usuario sube la imagen al inicio;
no se puede cambiar durante la misma sesión.
- **Solo carga desde disco**: input tipo `file`. No se implementa pegado de URLs.
- La foto puede ser JPEG, PNG o WEBP (formatos que admite `qwen-vl-plus`).
- **Sin límite de tamaño**: la app es de uso personal; no se impone restricción
  de peso en el frontend ni en el backend.

## Manejo de identificación incierta

Si `qwen-vl-plus` no logra identificar ingredientes con claridad (foto oscura,
imángulo raro, imagen que no es de comida), el agente **avanza de todas formas**
con lo que haya podido detectar e incluye una advertencia al usuario del tipo:
"Identifiqué estos ingredientes, aunque la imagen no era muy clara —
puede que me haya equivocado en alguno". La receta se genera normalmente.
| `uv venv` | Crea el virtualenv en `.venv/` |
| `uv add <pkg>` | Instala dependencias (registra en `pyproject.toml`) |
| `uv run <cmd>` | Ejecuta comandos dentro del virtualenv |

## Estructura de carpetas

```
photo-chef/
├── .env                  # API keys (NO commitear)
├── .env.example          # Plantilla pública de variables de entorno
├── .gitignore
├── pyproject.toml        # Dependencias Python (gestionado por uv)
├── specs/                # Documentación del proyecto
│   ├── mission.md
│   ├── roadmap.md
│   └── tech-stack.md
├── backend/
│   ├── main.py           # FastAPI app, rutas, StaticFiles
│   ├── agent.py          # Definición del agente LangGraph
│   └── tools.py          # Herramientas del agente (visión, búsqueda)
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── src/
    │   ├── App.svelte    # Componente raíz
    │   ├── lib/
    │   │   ├── Chat.svelte
    │   │   └── ImageUpload.svelte
    │   └── main.js
    └── dist/             # Build de producción (generado, no commitear)
```
