# Validation — Fase 7: Integración y producción

## Criterios de aceptación

### 1. Script `start.sh`

- [ ] El archivo `start.sh` existe en la raíz del proyecto
- [ ] `start.sh` tiene permisos de ejecución (`chmod +x`)
- [ ] Al ejecutar `./start.sh` desde la raíz, el frontend se compila sin errores
- [ ] `frontend/dist/index.html` existe tras ejecutar el script
- [ ] Si `npm run build` falla, el script termina con código de salida ≠ 0 y **no** arranca uvicorn
- [ ] El servidor arranca en `localhost:8005` al final del script

### 2. README.md

- [ ] `README.md` en la raíz describe el proyecto en una línea
- [ ] Incluye requisitos previos: Python ≥ 3.13 + `uv`, Node.js ≥ 20, `.env` con las dos claves API
- [ ] Incluye pasos para arrancar en **desarrollo** (backend con `--reload`, frontend con `npm run dev`)
- [ ] Incluye el comando de **producción** (`./start.sh`)

### 3. Integración estática (verificación manual)

- [ ] `GET http://localhost:8005/health` devuelve `{"status": "ok", "version": "0.1.0"}`
- [ ] `GET http://localhost:8005/` devuelve la app Svelte (HTML con `<title>Photo-Chef</title>`)
- [ ] Los assets del frontend (JS, CSS) cargan sin errores 404

### 4. Flujo end-to-end completo

- [ ] Cargar una foto de refrigerador → el agente emite eventos SSE de status ("Analizando…", "Buscando…", "Preparando…")
- [ ] La receta llega completa con formato Markdown (negritas, listas, cabeceras)
- [ ] El Markdown se renderiza correctamente en el frontend (no se muestra como texto plano)
- [ ] Hacer una pregunta de seguimiento → el agente responde coherentemente con la receta presentada
- [ ] El campo de imagen queda bloqueado después de enviarse la primera foto

### 5. Modo desarrollo (verificación de CORS)

- [ ] Con backend en `localhost:8005` y frontend en `localhost:5173`, las peticiones al `/chat` no producen errores CORS
- [ ] El SSE streaming funciona igual en modo dev que en producción

## Edge cases

- [ ] Si `frontend/dist/` no existe al arrancar con `uv run uvicorn` directamente (sin `start.sh`), el servidor arranca igualmente (sin montar static files) y responde en `/health`
- [ ] Una foto con formato no soportado (ej: `.gif`) recibe error 422 con mensaje descriptivo, tanto en dev como en producción
