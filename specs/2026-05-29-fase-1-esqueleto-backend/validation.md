# Validation — Fase 1: Esqueleto del backend

## Criterios de aceptación

La fase está completa y lista para merge cuando **todos** los siguientes puntos son verdaderos.

---

### ✅ 1. Dependencias instaladas

```bash
uv run python -c "import fastapi, uvicorn, dotenv; print('ok')"
# Debe imprimir: ok
```

- `pyproject.toml` lista `fastapi`, `uvicorn`, y `python-dotenv` como dependencias.

---

### ✅ 2. Servidor arranca sin errores

```bash
uv run uvicorn backend.main:app --port 8005 --reload
```

- Imprime `Uvicorn running on http://0.0.0.0:8005`.
- No hay excepciones ni warnings en el arranque.
- `Ctrl+C` detiene el servidor limpiamente.

---

### ✅ 3. Endpoint `/health` responde correctamente

```bash
curl -s http://localhost:8005/health
# Debe devolver:
# {"status":"ok","version":"0.1.0"}
```

- Código de estado HTTP: `200`.
- `Content-Type`: `application/json`.

---

### ✅ 4. CORS permite origen del frontend en desarrollo

```bash
curl -s -I -X OPTIONS http://localhost:8005/health \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET"
# La respuesta debe incluir:
# access-control-allow-origin: http://localhost:5173
```

---

### ✅ 5. Archivos estáticos montados

```bash
ls frontend/dist/
# Debe mostrar al menos: .gitkeep
```

- `frontend/dist/` existe en el repositorio (trackeado via `.gitkeep`).
- El servidor no lanza error al arrancar aunque `dist/` no tenga un `index.html`.

---

### ✅ 6. Estructura de archivos

```
backend/
  __init__.py   ← ya existía
  main.py       ← nuevo en esta fase
frontend/
  dist/
    .gitkeep    ← nuevo en esta fase
```

---

### ✅ 7. Variables de entorno cargadas

- `backend/main.py` llama a `load_dotenv()` al importarse.
- El servidor arranca sin error si `.env` existe con las claves definidas.
