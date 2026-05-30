# Requirements — Fase 7: Integración y producción

## Objetivo

Cerrar el MVP uniendo frontend compilado y backend en un único proceso FastAPI,
y documentar cómo arrancar la app en desarrollo. Tras esta fase, la app estará
lista para uso real con un solo comando.

## Contexto

- **Fases anteriores completadas**: 0–6. Backend funcional con SSE + LangGraph,
  frontend Svelte compilable en `frontend/`.
- **Static files ya implementado**: `backend/main.py` ya monta `frontend/dist/`
  con `StaticFiles` de forma condicional (solo si el directorio existe).
  No hay que tocar el backend en esta fase.
- **Prompt tuning**: fuera de scope — los prompts no se han ejecutado en producción
  real aún; cualquier ajuste se deja para una fase posterior.

## Decisiones

| Decisión | Elección | Motivo |
|---|---|---|
| Cómo lanzar build + servidor | Script `start.sh` | Un solo archivo ejecutable, sin dependencias extras |
| Contenido del README | Solo instrucciones de desarrollo | MVP local; no hay despliegue en la nube aún |
| Gestión de `frontend/dist/` | No se versiona (`.gitignore`) | Artefacto generado; se regenera con `start.sh` |

## Alcance

### Dentro de scope
- Crear `start.sh` (build frontend + arrancar backend)
- Escribir `README.md` con instrucciones de desarrollo
- Verificación manual del flujo completo end-to-end

### Fuera de scope
- Docker o contenerización
- CI/CD (GitHub Actions, etc.)
- Despliegue en la nube
- Ajuste fino de prompts (se deja para iteraciones futuras)
- Tests automáticos de integración nuevos
- Internacionalización o soporte multi-idioma adicional

## Restricciones técnicas

- Python ≥ 3.13, gestionado con `uv`
- Node.js ≥ 20 para el build de Svelte
- El script `start.sh` debe abortar si `npm run build` falla (no arrancar servidor con dist corrupto)
- El servidor debe arrancar en el puerto `8005` (fijado en el proyecto desde Fase 1)
- `.env` con `DASHSCOPE_API_KEY` y `TAVILY_API_KEY` es requisito previo del usuario,
  no se crea ni valida automáticamente por el script

## Referencia al stack

- Ver [tech-stack.md](../tech-stack.md) para versiones y configuración de puertos
- Ver [mission.md](../mission.md) para el flujo de usuario esperado
