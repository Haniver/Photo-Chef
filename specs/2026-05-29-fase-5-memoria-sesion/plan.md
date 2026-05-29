# Plan — Fase 5: Memoria de sesión

## 1. Singleton MemorySaver en el agente

- Crear instancia global `_memory = MemorySaver()` en `backend/agent.py`
- Pasar `checkpointer=_memory` a `create_react_agent` dentro de `build_agent`
- Añadir parámetro `image_b64: str | None` a `build_agent` para distinguir
  primera llamada (con imagen) de seguimiento (sin imagen)
- Cuando `image_b64 is None`, usar una herramienta stub `analyze_image_tool`
  que devuelve: "No se ha proporcionado imagen nueva. Usa el historial de
  conversación para responder." en lugar de llamar al modelo de visión

## 2. Endpoint `/chat` con imagen opcional

- Cambiar `image: UploadFile = File(...)` → `image: UploadFile | None = File(default=None)`
- Si `image` es None (seguimiento): omitir validación de formato y crear stub tool
- Si `image` está presente: comportamiento actual (validar, analizar, crear tool real)
- Ajustar el prompt del mensaje humano para distinguir:
  - Primera llamada: "Analiza mi refrigerador y sugiere una receta."
  - Seguimiento: mensaje de texto puro sin referencia a imagen

## 3. Actualizar el system prompt

- Añadir instrucción que indica al agente cómo comportarse en mensajes de seguimiento:
  "Si el historial ya contiene una receta, responde directamente las preguntas del
  usuario sin volver a analizar la imagen ni buscar recetas, a menos que el usuario
  pida explícitamente una nueva receta."

## 4. Pruebas

- Actualizar `tests/test_agent.py` para cubrir el flujo de seguimiento:
  - Primera petición con imagen → recibe receta
  - Segunda petición con texto → el agente responde con contexto
  - Verificar que `MemorySaver` retiene el thread entre instancias del agente
- Añadir prueba de que el stub tool devuelve el mensaje esperado cuando no hay imagen
