# Requirements — Fase 1: Esqueleto del backend

## Objetivo

Tener un servidor FastAPI arrancando en `localhost:8005` con un endpoint de salud,
CORS configurado para el frontend en desarrollo, y la carpeta de estáticos montada.
Esta fase establece la base sobre la que se construirán todos los endpoints futuros.

## Decisiones tomadas

| Decisión | Valor |
|---|---|
| Punto de entrada | `backend/main.py` |
| Puerto | `8005` |
| Respuesta de `/health` | `{"status": "ok", "version": "0.1.0"}` |
| Comando de arranque | `uv run uvicorn backend.main:app --port 8005 --reload` |
| Archivos estáticos | Montados en `/` desde `frontend/dist/` ya en esta fase |

## Dependencias a instalar

```
fastapi
uvicorn[standard]
python-dotenv
```

Instaladas con `uv add`.

## Configuración de CORS

Origen permitido: `http://localhost:5173` (Vite dev server).
Métodos: `GET`, `POST`, `OPTIONS`.
Cabeceras: `Content-Type`, `Authorization`.

## Archivos estáticos

`frontend/dist/` se monta con `StaticFiles(directory="frontend/dist", html=True)`.
El parámetro `html=True` hace que FastAPI sirva `index.html` como fallback para
rutas desconocidas, lo que es necesario para el router del lado del cliente.
El directorio se crea en esta fase con un `.gitkeep`; habrá contenido real en Fase 7.

## Variables de entorno

En esta fase solo se carga el `.env` para confirmar que `python-dotenv` funciona.
Las claves (`DASHSCOPE_API_KEY`, `TAVILY_API_KEY`) no se usan todavía.

## Fuera de alcance

- Cualquier lógica de negocio (visión, recetas, agente).
- Autenticación o autorización.
- Endpoints distintos a `/health`.
- Build del frontend.
- Despliegue en producción.
