# Validation — Fase 2: Pipeline de visión

## Criterios de aceptación

La fase está completa y lista para merge cuando **todos** los siguientes puntos son verdaderos.

---

### ✅ 1. Dependencias instaladas

```bash
uv run python -c "import langchain_qwq; print('ok')"
# Debe imprimir: ok
```

- `pyproject.toml` lista `langchain-qwq` como dependencia.

---

### ✅ 2. Endpoint existe y el servidor arranca

```bash
uv run uvicorn backend.main:app --port 8005 --reload
```

- El servidor arranca sin errores.
- La ruta `POST /analyze-image` aparece en `http://localhost:8005/docs`.

---

### ✅ 3. Imagen válida devuelve ingredientes

```bash
# Convertir cualquier JPEG a base64 y enviar
IMAGE_B64=$(base64 -w 0 foto_fridge.jpg)
curl -s -X POST http://localhost:8005/analyze-image \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$IMAGE_B64\"}" | python3 -m json.tool
```

- Código HTTP: `200`.
- La respuesta tiene la forma:
  ```json
  {
    "ingredients": [
      { "name": "...", "confidence": 0.0 }
    ],
    "low_confidence": false
  }
  ```
- `ingredients` contiene al menos un elemento con los campos `name` y `confidence`.
- `confidence` es un número entre `0.0` y `1.0`.

---

### ✅ 4. Imagen PNG y WEBP también son aceptadas

- Repetir el test del punto 3 con una imagen `.png` y con una `.webp`.
- Ambas devuelven HTTP `200` con ingredientes.

---

### ✅ 5. Formato no soportado devuelve error claro

```bash
# Enviar un PDF o un GIF cualquiera en base64
IMAGE_B64=$(base64 -w 0 documento.pdf)
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8005/analyze-image \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$IMAGE_B64\"}"
# Debe devolver: 422
```

- Código HTTP: `422`.
- El body de respuesta incluye `"detail"` con texto descriptivo sobre los formatos aceptados.

---

### ✅ 6. Imagen ambigua activa `low_confidence`

- Enviar una foto muy oscura, borrosa, o que no sea de un refrigerador.
- La respuesta tiene `"low_confidence": true`.
- El código HTTP sigue siendo `200`.
- `ingredients` puede ser una lista vacía o contener ingredientes con confianza baja.

---

### ✅ 7. Prueba manual con foto real

- Tomar o buscar una foto real del interior de un refrigerador con varios ingredientes.
- Enviar la foto al endpoint.
- Verificar manualmente que los ingredientes devueltos corresponden razonablemente
  a lo visible en la foto.
- Al menos 3 ingredientes deben ser correctamente identificados.

---

### 8. `DASHSCOPE_API_KEY` faltante devuelve error claro

- Renombrar temporalmente `.env` a `.env.bak` y reiniciar el servidor.
- Intentar llamar al endpoint.
- El servidor devuelve un error HTTP (500 o 503) con mensaje descriptivo,
  **no** un `KeyError` sin manejar ni un traceback expuesto al cliente.
- Restaurar `.env` al terminar la verificación.
