# Requirements — Fase 6: Frontend Svelte

## Objetivo

Implementar la interfaz web de Photo-Chef: una app de una sola página que permite
al usuario cargar una foto del refrigerador, recibir una receta completa con
streaming en tiempo real, y hacer preguntas de seguimiento sobre esa receta.

## Tecnología

| Capa | Decisión |
|---|---|
| Framework UI | Svelte 5 con **runes syntax** (`$state`, `$derived`, `$effect`) |
| Build tool | Vite 6.x |
| Lenguaje | TypeScript |
| Markdown rendering | `marked` + `DOMPurify` (sanitizar output del LLM) |
| Comunicación backend | `fetch` con `ReadableStream` o `EventSource` (SSE) |
| Fuente tipográfica | `Inter` |

## Funcionalidad requerida

### Carga de imagen
- Input de tipo `file` con accept `image/jpeg,image/png,image/webp`
- Vista previa de la imagen seleccionada antes de enviar
- El input se bloquea visualmente una vez que la conversación comienza;
  no se puede cambiar la imagen durante la sesión
- Si se intenta subir un formato no soportado, se muestra un mensaje de error inline
  (no alert nativo del navegador)

### Chat
- El usuario puede escribir texto libre en un campo de entrada y enviar mensajes
- El primer mensaje inicia la sesión; si el usuario ya subió una imagen,
  se incluye en base64 junto con el texto (o con texto vacío si no escribió nada)
- Los mensajes subsiguientes son solo texto (imagen bloqueada)
- Las respuestas del agente se renderizan con Markdown (negritas, listas, cabeceras, emojis)
  sanitizado con DOMPurify

### Streaming
- Los tokens del LLM llegan via SSE evento `token` y se añaden progresivamente
  al final de la burbuja del agente activa
- Los mensajes de estado llegan via evento `status` y se muestran como texto
  informativo sobre la burbuja del agente en construcción
- Un indicador de escritura (tres puntos animados) es visible mientras llegan tokens
- Al completarse la respuesta, el indicador desaparece y el contenido queda fijo

### Sesión
- `session_id`: UUID generado con `crypto.randomUUID()` al cargar la página,
  mantenido en memoria; se pierde al recargar o cerrar la pestaña (by design)
- El `session_id` se envía en cada petición al backend

### Manejo de errores
- Imagen inválida (formato): mensaje inline en el componente de carga
- Error HTTP del backend (≥ 400): burbuja de error en el chat con texto legible
- Pérdida de conexión / timeout: mensaje de error en el chat con sugerencia de reintento
- No se usan `alert()` ni `confirm()` del navegador

## Diseño visual

| Parámetro | Valor |
|---|---|
| Modo | Light mode únicamente |
| Ancho máximo del contenido | 720 px, centrado |
| Color de acento principal | Naranja terracota `#E8622A` |
| Color de acento secundario | Verde salvia `#6B8F6B` |
| Fondos | Cremas / blancos cálidos |
| Tipografía | `Inter` (UI general) |
| Título / nombre del chatbot | **Photo-Chef** |

No se usan degradados morados ni paletas frías.

## Estructura de archivos esperada

```
frontend/
  package.json
  vite.config.ts
  tsconfig.json
  src/
    app.css           # variables CSS globales + reset
    App.svelte        # shell principal, genera session_id
    lib/
      api.ts          # sendMessage(), parseo de SSE
    components/
      ImageUpload.svelte
      ChatWindow.svelte
      ChatBubble.svelte
      StatusMessage.svelte
      TypingIndicator.svelte
  index.html
```

## Fuera de alcance

- Dark mode
- Drag-and-drop para la imagen
- Persistencia de historial entre sesiones
- Soporte para múltiples imágenes por sesión
- Autenticación de usuarios
- PWA / service workers
- Internacionalización (i18n); el idioma lo controla el backend según el texto enviado

## Dependencias con otras fases

- El backend (Fases 1–5) debe estar corriendo en `localhost:8005` con el endpoint
  `POST /api/chat` que acepta `{ session_id, message, image? }` y responde con SSE
- FastAPI debe servir `frontend/dist/` en la raíz `/` (configurado en Fase 1)
