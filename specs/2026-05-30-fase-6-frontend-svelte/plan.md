# Plan — Fase 6: Frontend Svelte

## 1. Scaffolding del proyecto

- Inicializar proyecto Svelte 5 + Vite + TypeScript dentro de `frontend/`
  usando `npm create svelte@latest .` (o `npm create vite@latest . -- --template svelte-ts`)
- Configurar `vite.config.ts` con proxy al backend (`/api → http://localhost:8005`)
  para el servidor de desarrollo
- Instalar dependencias de UI: `marked`, `dompurify`, `@types/dompurify`
- Verificar que `npm run dev` arranca sin errores en `localhost:5173`
- Verificar que `npm run build` genera `frontend/dist/` sin errores

## 2. Shell de la aplicación

- Crear `App.svelte` como raíz de la aplicación:
  - Layout de una sola columna, ancho máximo 720 px, centrado
  - Tipografía `Inter` (cargada desde Google Fonts o self-hosted)
  - Paleta CSS: variables de color para crema, naranja terracota `#E8622A` y verde salvia `#6B8F6B`
  - Título de cabecera "Photo-Chef" visible en todo momento
- Generar `session_id` como UUID al cargar la página (usando `crypto.randomUUID()`)
  y mantenerlo en memoria durante la sesión

## 3. Componente ImageUpload

- Aceptar solo `image/jpeg`, `image/png`, `image/webp` en el `<input type="file">`
- Mostrar preview de la imagen seleccionada antes de enviar
- Convertir la imagen a base64 para incluirla en el primer mensaje al agente
- Una vez iniciada la conversación, deshabilitar y bloquear visualmente el input
  para que no se pueda cambiar la imagen durante la sesión
- Mostrar mensaje de error claro si el usuario intenta subir un formato no soportado

## 4. Componente ChatWindow

- Renderizar lista de mensajes con dos estilos de burbuja:
  - Burbuja usuario: alineada a la derecha, fondo acento terracota/claro
  - Burbuja agente: alineada a la izquierda, fondo crema/neutro
- El mensaje actual del agente se construye progresivamente conforme llegan tokens
- Hacer scroll automático al último mensaje cuando llega contenido nuevo
- Renderizar el contenido de burbujas del agente como Markdown
  usando `marked` + sanitización con `DOMPurify`

## 5. Mensajes de estado e indicador de escritura

- Componente `StatusMessage`: muestra los mensajes de estado recibidos via evento SSE `status`
  (p.ej. "Analizando tu refrigerador…", "Buscando recetas en internet…",
  "Preparando tu receta…") como texto informativo sobre la burbuja del agente activa
- Componente `TypingIndicator`: animación de tres puntos pulsantes visible
  mientras llegan tokens del agente; desaparece al completarse la respuesta

## 6. Integración SSE / EventSource

- Crear módulo `src/lib/api.ts` que encapsula la comunicación con el backend:
  - Función `sendMessage(sessionId, userText, imageBase64?)` que abre un `EventSource`
    (o usa `fetch` con `ReadableStream`) hacia `POST /api/chat`
  - Parsear eventos `status` y `token` e invocar callbacks para actualizar el estado
  - Manejar el evento `close` / `error` del stream para detectar fin de respuesta
    o errores de red
- El primer mensaje incluye la imagen en base64; los mensajes de seguimiento
  solo contienen texto

## 7. Manejo de errores

- Imagen con formato no soportado: mostrar alerta inline en el componente ImageUpload
- Error del agente o respuesta HTTP ≥ 400: mostrar burbuja de error en el chat
  con texto legible para el usuario
- Timeout o pérdida de conexión: mostrar mensaje de reintento sugerido

## 8. Build y verificación de integración

- `npm run build` genera `frontend/dist/` con el bundle final
- Verificar que FastAPI sirve correctamente `frontend/dist/` al acceder a `http://localhost:8005/`
- Prueba de humo end-to-end: cargar imagen → recibir receta completa
