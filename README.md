# Photo-Chef

Toma una foto de tu refrigerador y recibe una receta hecha con lo que tienes.

## Requisitos previos

- Python ≥ 3.13 y [`uv`](https://docs.astral.sh/uv/)
- Node.js ≥ 20
- Archivo `.env` en la raíz con las siguientes claves:

```
DASHSCOPE_API_KEY=<tu clave de Alibaba Dashscope>
TAVILY_API_KEY=<tu clave de Tavily>
```

## Desarrollo

Arranca backend y frontend por separado en dos terminales:

```bash
# Terminal 1 — backend (con recarga automática)
uv run uvicorn backend.main:app --port 8005 --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

La app estará disponible en `http://localhost:5173` (frontend dev server).

## Producción

Compila el frontend y arranca el servidor con un solo comando:

```bash
./start.sh
```

La app estará disponible en `http://localhost:8005`.

## API

### `GET /health`
Devuelve `{"status": "ok", "version": "0.1.0"}`.

### `POST /chat` — SSE streaming

Endpoint principal. Acepta `multipart/form-data`:

| Campo | Tipo | Descripción |
|---|---|---|
| `image` | file (JPEG/PNG/WEBP) | Foto del refrigerador |
| `message` | string (opcional) | Texto del usuario |
| `session_id` | string (opcional) | ID de sesión para memoria de conversación |

Devuelve `text/event-stream` con eventos `status`, `token` y `done`.

```bash
curl -N -X POST http://localhost:8005/chat \
  -F "image=@fridge.jpg" \
  -F "session_id=mi-sesion"
```

## Tests

```bash
uv run pytest
```
