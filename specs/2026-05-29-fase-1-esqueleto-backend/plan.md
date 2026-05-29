# Plan — Fase 1: Esqueleto del backend

## 1. Dependencias

- Agregar `fastapi`, `uvicorn`, y `python-dotenv` al proyecto con `uv add`.

## 2. Módulo principal

- Crear `backend/main.py` con la instancia de la app FastAPI.
- Cargar variables de entorno desde `.env` con `python-dotenv` al arrancar.

## 3. Endpoint de salud

- Implementar `GET /health` que devuelve `{"status": "ok", "version": "0.1.0"}`.

## 4. CORS

- Configurar `CORSMiddleware` para permitir peticiones desde `http://localhost:5173`
  (dev server de Svelte) con los métodos y cabeceras necesarios.

## 5. Archivos estáticos del frontend

- Montar `frontend/dist/` en la raíz `/` como `StaticFiles` con `html=True`.
- Crear `frontend/dist/.gitkeep` para que el directorio exista en el repo
  antes de que haya un build real.

## 6. Verificación manual

- Arrancar el servidor con `uv run uvicorn backend.main:app --port 8005 --reload`.
- Confirmar `GET /health` en el navegador o con `curl`.
- Confirmar que el servidor arranca sin errores aunque `frontend/dist/` esté vacío.
