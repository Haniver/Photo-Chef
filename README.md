# Photo-Chef

Photo-Chef identifica los ingredientes de tu refrigerador a partir de una foto y sugiere una receta.

## Instalación

```bash
uv sync
cp .env.example .env   # añade DASHSCOPE_API_KEY y TAVILY_API_KEY
```

## Ejecución

```bash
uv run uvicorn backend.main:app --port 8005
```

## API

### `GET /health`
Comprueba que el servidor está corriendo.

### `POST /analyze-image`
Analiza una imagen de refrigerador.  
Body JSON: `{"image": "<base64>"}` → devuelve lista de ingredientes.

### `POST /recipe`
Genera una receta a partir de ingredientes.  
Body JSON: `{"ingredients": [{"name": "...", "confidence": 0.9}]}` → devuelve Markdown.

### `POST /chat` — SSE streaming
Endpoint principal. Acepta `multipart/form-data`:

| Campo | Tipo | Descripción |
|---|---|---|
| `image` | file (JPEG/PNG/WEBP) | Foto del refrigerador |
| `message` | string (opcional) | Texto del usuario |
| `session_id` | string (opcional) | ID de sesión (stub, Fase 5) |

Devuelve un stream `text/event-stream` con tres tipos de eventos:

```
event: status
data: {"message": "Analizando tu refrigerador…"}

event: token
data: {"text": "## Tortilla de patatas\n"}

event: done
data: {}
```

Ejemplo con `curl`:
```bash
curl -N -X POST http://localhost:8005/chat \
  -F "image=@/ruta/a/fridge.jpg" \
  -F "message=" \
  -F "session_id=test"
```

## Tests

```bash
uv run pytest
```
