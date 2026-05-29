# Requirements — Fase 3: Búsqueda de recetas

## Objetivo

Implementar la capa de búsqueda y síntesis que convierte una lista de ingredientes
en una receta presentada en Markdown. Esta fase cierra el pipeline de datos del backend
y expone el endpoint que el frontend usará (en fases posteriores).

## Contexto

- **Misión**: dado que el usuario ya tiene sus ingredientes identificados (Fase 2),
  el siguiente paso es encontrar una receta útil y presentarla claramente.
- **Posición en el roadmap**: Fase 3 de 7. El agente LangGraph completo se construye
  en Fase 4; aquí se construyen las funciones que ese agente usará como herramientas.

## Alcance

### Incluido
- Instalación y configuración de `langchain-tavily`.
- Función `search_recipes` en `backend/search.py`.
- Función `synthesize_recipe` en `backend/recipe.py`.
- Endpoint `POST /recipe` en `backend/main.py`.
- Suite de tests unitarios y de integración en `tests/test_recipe.py`.
- Documentación de `TAVILY_API_KEY` en el `README`.

### Excluido (fuera de scope)
- Agente LangGraph ReAct (Fase 4).
- Streaming SSE de tokens (Fase 4).
- Memoria de sesión / preguntas de seguimiento (Fase 5).
- Cualquier componente de frontend (Fase 6).
- Planificación de comidas, listas de compras, o reconocimiento de cantidades.

## Decisiones de diseño

| Decisión | Elección | Razón |
|---|---|---|
| Número de resultados Tavily | 3 | Equilibrio entre coste y contexto para la síntesis |
| Formato de respuesta del endpoint | Markdown como string | Flexible para el frontend; el LLM ya genera Markdown bien formateado |
| Modelo de síntesis | `qwen3.5-flash` con `thinking_budget=200` | Especificado en el roadmap; adecuado para síntesis sin coste alto de razonamiento |
| Estrategia de síntesis | Dos pasos (búsqueda → síntesis) | Más trazable; permite testear cada función por separado; el LLM recibe contexto completo |
| Ingredientes de baja confianza | Se incluyen con advertencia visible | Alineado con la misión: no bloquear al usuario si la foto es poco clara |

## Restricciones técnicas

- `DASHSCOPE_API_KEY` ya existe en `.env` (Fase 2); solo añadir `TAVILY_API_KEY`.
- `langchain-qwq` ya está instalado (Fase 2); no reinstalar.
- El servidor sigue corriendo en `localhost:8005`.
- Python 3.11+ (fijado en Fase 0).
- Tests deben correr sin conexión a APIs reales (usando mocks);
  los tests de integración real son opcionales y se marcan con `@pytest.mark.integration`.

## Dependencias nuevas

```
langchain-tavily       # búsqueda web
pytest                 # runner de tests (si no está ya)
pytest-asyncio         # soporte async para los tests del endpoint
httpx                  # cliente HTTP para los tests del endpoint FastAPI
```
