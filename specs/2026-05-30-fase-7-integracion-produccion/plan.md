# Plan — Fase 7: Integración y producción

## 1. Script `start.sh`

- Crear `start.sh` en la raíz del proyecto
- Pasos que ejecuta en orden:
  1. `cd frontend && npm install` — instala dependencias del frontend si hace falta
  2. `npm run build` — compila Svelte a `frontend/dist/`
  3. Si el build falla, abortar con mensaje de error claro (no arrancar el servidor)
  4. `cd ..` y arrancar `uv run uvicorn backend.main:app --port 8005`
- Hacer el script ejecutable (`chmod +x start.sh`)
- Verificar que `frontend/dist/` no está en `.gitignore` de forma incorrecta
  (debería estar ignorado: solo el `dist/` generado no se versiona)

## 2. README.md

- Escribir (o reemplazar) `README.md` en la raíz con:
  - **Descripción breve** del proyecto (una línea)
  - **Requisitos previos**: Python ≥ 3.13 + `uv`, Node.js ≥ 20, claves API en `.env`
    (`DASHSCOPE_API_KEY`, `TAVILY_API_KEY`)
  - **Cómo arrancar en desarrollo**:
    - Backend: `uv run uvicorn backend.main:app --port 8005 --reload`
    - Frontend: `cd frontend && npm run dev`
  - **Build de producción**: `./start.sh`

## 3. Verificación end-to-end

- Correr `./start.sh` desde la raíz y confirmar que termina sin errores
- Verificar que `frontend/dist/index.html` existe tras el build
- Abrir `http://localhost:8005` y confirmar que sirve la app Svelte
- Verificar que `GET /health` responde `{"status": "ok"}`
- Hacer prueba manual completa:
  1. Cargar imagen de refrigerador → recibir receta completa con streaming
  2. Hacer al menos una pregunta de seguimiento → respuesta coherente con contexto
- Verificar que en modo dev (frontend en `localhost:5173`, backend en `localhost:8005`) el CORS sigue funcionando
