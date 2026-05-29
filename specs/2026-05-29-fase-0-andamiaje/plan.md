# Plan — Fase 0: Andamiaje del proyecto

## 1. Inicializar el proyecto con uv

- Ejecutar `uv init` en la raíz del repositorio para generar `pyproject.toml`
- Fijar la versión de Python a 3.13 en `pyproject.toml` (`requires-python = ">=3.13"`)
- Crear el virtualenv con `uv venv --python 3.13`
- Verificar que `.venv/` se crea correctamente y que `python --version` dentro del env devuelve 3.13.x

## 2. Validar y ajustar el .env

- Confirmar que `.env` contiene `DASHSCOPE_API_KEY` y `TAVILY_API_KEY` con valores reales
- Crear `.env.example` en la raíz con las mismas variables pero sin valores reales,
  para documentar qué keys necesita el proyecto:
  ```
  DASHSCOPE_API_KEY=your_dashscope_api_key_here
  TAVILY_API_KEY=your_tavily_api_key_here
  ```
- Confirmar que `.gitignore` excluye `.env` (ya presente)

## 3. Crear la estructura de carpetas

- Crear `backend/` con un `__init__.py` vacío
- Crear `frontend/` vacío (se poblará en Fase 6)
- La carpeta `specs/` ya existe

## 4. Validar el .gitignore

- Confirmar que `.gitignore` cubre: `.env`, `.venv/`, `__pycache__/`, `*.pyc`,
  `frontend/node_modules/`, `frontend/dist/`
- El `.gitignore` actual ya cubre todos estos puntos; no requiere cambios

## 5. Primer commit del andamiaje

- Stage: `pyproject.toml`, `.python-version` (si uv lo genera), `backend/__init__.py`,
  `frontend/` (si git admite carpeta vacía con `.gitkeep`), `.env.example`
- Mensaje de commit: `chore: fase 0 — andamiaje inicial del proyecto`
- Push a la rama `feat/fase-0-andamiaje` en el remote de GitHub
