# Requirements — Fase 0: Andamiaje del proyecto

## Alcance

Esta fase establece la base técnica del repositorio antes de escribir cualquier
código de producto. Su único propósito es garantizar que cualquier colaborador
(o la propia máquina de desarrollo en el futuro) pueda clonar el repo, ejecutar
un solo comando y tener el entorno listo para trabajar.

## Decisiones tomadas

| Decisión | Valor | Razón |
|---|---|---|
| Gestión de dependencias | `uv` | Velocidad, lockfile determinista, manejo de versiones de Python integrado |
| Versión de Python | 3.13 | Versión más reciente estable; elegida explícitamente por el usuario |
| Puerto del backend | 8005 | Los puertos 8000 y 8001 están ocupados en la máquina de desarrollo (ver tech-stack.md) |
| Estructura de carpetas | `backend/`, `frontend/`, `specs/` | Separación clara de responsabilidades; FastAPI sirve el build de Svelte en producción |
| Remote | GitHub | Ya configurado |

## Estado previo detectado

Los siguientes artefactos ya existen en la raíz del repo y **no requieren cambios**:

- `.gitignore` — cubre `.env`, `.venv/`, `__pycache__/`, `frontend/node_modules/`, `frontend/dist/`
- `.env` — contiene `DASHSCOPE_API_KEY` y `TAVILY_API_KEY` con valores reales.
  También contiene claves de proyectos anteriores (`OPENAI_API_KEY`, `LANGSMITH_API_KEY`, etc.)
  que son ignoradas por Photo-Chef y no causan conflicto.
- `.git/` — repositorio inicializado con remote en GitHub

Los siguientes artefactos **no existen aún** y son el objetivo de esta fase:

- `pyproject.toml` (generado por `uv init`)
- `.venv/` (generado por `uv venv`)
- `backend/` con `__init__.py`
- `frontend/` (carpeta vacía o con `.gitkeep`)
- `.env.example` (plantilla pública del .env)

## Fuera de alcance

- Instalar dependencias de FastAPI, LangGraph u otros paquetes (Fase 1+)
- Configurar Svelte/Vite (Fase 6)
- Escribir ningún endpoint ni lógica de negocio
- Configurar CI/CD o entornos de producción en la nube

## Contexto del proyecto

Photo-Chef es una app que recibe una foto del refrigerador, identifica ingredientes
con visión por computadora (`qwen-vl-plus` vía Dashscope) y sugiere recetas buscadas
en internet (Tavily). Ver `specs/mission.md` para el flujo completo y
`specs/tech-stack.md` para las decisiones tecnológicas.
