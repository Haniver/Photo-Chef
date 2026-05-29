# Requirements — Fase 2: Pipeline de visión

## Objetivo

Añadir al backend la capacidad de analizar una imagen de refrigerador y devolver
la lista de ingredientes visibles, usando el modelo multimodal `qwen-vl-plus`
de Alibaba Dashscope vía el endpoint OpenAI-compatible.

---

## Contrato del endpoint

### `POST /analyze-image`

**Request body (JSON):**

```json
{
  "image": "<base64 string de la imagen>"
}
```

La cadena base64 representa el contenido binario del archivo de imagen directamente,
sin prefijo de data URI (`data:image/jpeg;base64,...`).

**Response body (JSON, HTTP 200):**

```json
{
  "ingredients": [
    { "name": "tomate", "confidence": 0.9 },
    { "name": "queso", "confidence": 0.75 }
  ],
  "low_confidence": false
}
```

- `ingredients`: lista de ingredientes detectados, cada uno con nombre y confianza estimada.
- `low_confidence`: `true` si el modelo indica incertidumbre general sobre la imagen
  (poca iluminación, imagen borrosa, contenido poco claro). El endpoint devuelve HTTP 200
  igualmente; es el consumidor quien decide cómo presentar la advertencia al usuario.

**Error (HTTP 422) — formato de imagen no soportado:**

```json
{
  "detail": "Formato de imagen no soportado. Se acepta JPEG, PNG o WEBP."
}
```

---

## Validación de formato

- Se detecta el formato por magic number (primeros bytes tras decodificar el base64),
  no por extensión ni por el campo `Content-Type`.
- Formatos aceptados: **JPEG** (`FFD8FF`), **PNG** (`89504E47`), **WEBP** (`RIFF....WEBP`).
- Cualquier otro formato devuelve HTTP 422 con el detalle anterior.
- No se valida el tamaño de la imagen; se confía en los límites del API de Dashscope.

---

## Integración con Dashscope

- Se usa `ChatQwen` de `langchain-qwq`:
  - `model`: `qwen-vl-plus`
  - `api_key`: variable de entorno `DASHSCOPE_API_KEY`
- El prompt pide al modelo una lista estructurada de ingredientes con su nivel
  de confianza estimado.

---

## Librería

- Dependencia: `langchain-qwq` (no `langchain-openai` ni `openai`).

---

## Estructura de archivos nueva en esta fase

```
backend/
  vision.py     ← lógica de análisis de imagen (nuevo)
  main.py       ← se modifica para agregar el endpoint y cargar DASHSCOPE_API_KEY
```

---

## Fuera de alcance

- Streaming de la respuesta de visión (se hace en Fase 4).
- Caché de resultados por imagen.
- Soporte para URLs de imagen (solo base64 en esta fase).
- Límites de tamaño de imagen en el backend.
- Tests automatizados (la prueba es manual con foto real).

