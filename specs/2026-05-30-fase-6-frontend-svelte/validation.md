# Validation — Fase 6: Frontend Svelte

## Criterios de aceptación

### Build y arranque

- ✅ `npm run build` (dentro de `frontend/`) completa sin errores ni warnings fatales
- ✅ `npm run dev` arranca en `localhost:5173` sin errores en consola
- [ ] Accediendo a `http://localhost:8005/` (backend + dist) se carga la app correctamente

### Apariencia general

- ✅ El título "Photo-Chef" es visible en la cabecera en todo momento
- ✅ El contenido tiene un ancho máximo de 720 px y está centrado en pantallas anchas
- ✅ La paleta usa tonos cálidos (crema, terracota `#E8622A`, verde salvia `#6B8F6B`);
      no hay azules ni morados prominentes
- ✅ La tipografía es `Inter` o una sans-serif similar en ausencia de conexión a fonts.google.com

### Componente de carga de imagen

- ✅ El input de archivo solo acepta JPEG, PNG y WEBP; intentar subir un PDF, GIF
      u otro formato muestra un mensaje de error inline (sin alert nativo)
- ✅ Al seleccionar una imagen válida se muestra el preview inmediatamente
- ✅ Una vez enviada la primera imagen, el input y el botón de carga están deshabilitados
      y muestran un estado visual de bloqueado
- ✅ No es posible enviar un mensaje sin haber seleccionado una imagen primero

### Chat — flujo principal

- ✅ Al enviar la imagen (con o sin texto), aparece una burbuja de usuario en el chat
- ✅ Aparecen mensajes de estado ("Analizando tu refrigerador…",
      "Buscando recetas en internet…", "Preparando tu receta…") antes o durante
      la respuesta del agente
- ✅ La respuesta del agente se construye token a token (streaming visible),
      sin esperar a que la respuesta completa llegue
- ✅ El indicador de escritura (puntos animados) es visible mientras llegan tokens
      y desaparece al completarse la respuesta
- ✅ La respuesta final del agente tiene Markdown renderizado:
      negritas (`**texto**`), listas (`-` o `1.`), cabeceras (`##`), emojis

### Chat — conversación de seguimiento

- ✅ Después de recibir la receta, el campo de texto está habilitado
- ✅ Enviar una pregunta de seguimiento (sin imagen) genera una nueva burbuja
      de usuario y el agente responde con contexto de la receta
- [ ] Al menos 3 turnos de seguimiento funcionan sin errores

### Sesión

- ✅ `session_id` se genera al cargar la página
- ✅ Al recargar la página se genera un nuevo `session_id` (sesión nueva)
- ✅ Dos pestañas abiertas simultáneamente tienen `session_id` distintos

### Sanitización de Markdown

- ✅ El contenido del agente con `<script>alert(1)</script>` incrustado en Markdown
      no ejecuta el script (DOMPurify lo elimina)
- ✅ Los ataques de tipo `<img src=x onerror=alert(1)>` en la respuesta del agente
      no ejecutan código JavaScript

### Manejo de errores

- ✅ Si el backend devuelve un error HTTP (p.ej. 422 o 500), aparece una burbuja
      de error con mensaje legible en el chat
- ✅ Si la conexión SSE se interrumpe abruptamente, aparece un mensaje de error
      en el chat (no se queda el indicador de escritura colgado indefinidamente)

### Integración con el backend

- [ ] Flujo end-to-end completo: foto de refrigerador real → receta completa en ~30 s
- [ ] La receta se muestra con formato Markdown (negritas, listas de ingredientes, pasos)
- [ ] Tres preguntas de seguimiento ("¿a qué temperatura?", "¿puedo sustituir X?",
      "¿cuánto tiempo tarda?") reciben respuestas coherentes con la receta

## Pasos de verificación manual

1. Arrancar backend: `uv run uvicorn backend.main:app --port 8005`
2. Arrancar frontend dev: `cd frontend && npm run dev`
3. Abrir `http://localhost:5173`
4. Subir una foto de refrigerador con ingredientes variados
5. Verificar que los mensajes de estado aparecen en orden correcto
6. Verificar que la receta llega en streaming y se renderiza con Markdown
7. Hacer 3 preguntas de seguimiento y verificar coherencia
8. Recargar la página y verificar que la sesión se reinicia (imagen desbloqueada, chat vacío)
9. Probar con imagen en formato PDF → verificar error inline
10. Construir para producción: `npm run build`, luego visitar `http://localhost:8005/`
    y repetir pasos 4–7
