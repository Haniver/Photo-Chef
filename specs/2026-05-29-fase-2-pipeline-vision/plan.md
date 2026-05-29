# Plan — Fase 2: Pipeline de visión

## 1. Instalar dependencias

- Agregar `langchain-qwq` con `uv add`
- Verificar que `DASHSCOPE_API_KEY` esté presente en `.env` y se cargue en `main.py`

## 2. Cliente LLM de visión

- Crear `backend/vision.py`
- Instanciar `ChatQwen` de `langchain_qwq`:
  - `model="qwen-vl-plus"`
  - `api_key` leída de la variable de entorno `DASHSCOPE_API_KEY`
- Implementar función `analyze_image(image_b64: str) -> dict`:
  - Construye un mensaje multimodal con la imagen en base64
  - Pide al modelo que devuelva la lista de ingredientes visibles
  - Parsea la respuesta y detecta baja confianza
  - Devuelve `{"ingredients": [{"name": str, "confidence": float}], "low_confidence": bool}`

## 3. Validación de formato de imagen

- Implementar función `validate_image_format(image_b64: str) -> str`:
  - Decodifica los primeros bytes del base64 para leer el magic number
  - Acepta JPEG (`FFD8FF`), PNG (`89504E47`), WEBP (`52494646...57454250`)
  - Lanza `ValueError` con mensaje descriptivo para cualquier otro formato

## 4. Endpoint `POST /analyze-image`

- Definir modelo Pydantic `AnalyzeImageRequest` con campo `image: str` (base64)
- Definir modelo Pydantic `Ingredient` con `name: str` y `confidence: float`
- Definir modelo Pydantic `AnalyzeImageResponse` con `ingredients: list[Ingredient]`
  y `low_confidence: bool`
- Registrar el endpoint en `main.py`:
  - Llama a `validate_image_format`; si falla, devuelve HTTP 422 con detalle del error
  - Llama a `analyze_image`
  - Devuelve `AnalyzeImageResponse`

## 5. Prueba manual

- Enviar una foto real de un refrigerador al endpoint usando `curl` o un script Python
- Verificar que los ingredientes detectados son razonables
- Verificar comportamiento con imagen de baja calidad o poca iluminación
