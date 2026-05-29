import base64
import json
import os
import re

from langchain_core.messages import HumanMessage
from langchain_qwq import ChatQwen

_MIME_TYPES = {
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


def _detect_format(image_b64: str) -> str:
    """Detect image format from magic bytes. Returns 'jpeg', 'png', or 'webp'."""
    try:
        # 16 base64 chars → 12 bytes, enough for all magic number checks
        header = base64.b64decode(image_b64[:16])
    except Exception:
        raise ValueError("Formato de imagen no soportado. Se acepta JPEG, PNG o WEBP.")

    if header[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if header[:4] == b"\x89PNG":
        return "png"
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "webp"

    raise ValueError("Formato de imagen no soportado. Se acepta JPEG, PNG o WEBP.")


def validate_image_format(image_b64: str) -> str:
    """Validate and return the image format. Raises ValueError for unsupported formats."""
    return _detect_format(image_b64)


def analyze_image(image_b64: str) -> dict:
    """Analyze a base64 image and return detected ingredients.

    Returns:
        {
            "ingredients": [{"name": str, "confidence": float}],
            "low_confidence": bool,
        }
    """
    fmt = _detect_format(image_b64)
    mime = _MIME_TYPES[fmt]

    llm = ChatQwen(
        model="qwen-vl-plus",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
    )

    prompt = (
        "Analiza esta imagen del interior de un refrigerador. "
        "Lista todos los ingredientes o alimentos visibles. "
        "Para cada ingrediente, estima tu nivel de confianza entre 0.0 (muy incierto) y 1.0 (muy seguro). "
        "Si la imagen es oscura, borrosa, o no muestra claramente un refrigerador con alimentos, "
        "indica baja confianza general con low_confidence=true. "
        "Responde ÚNICAMENTE con un objeto JSON con esta estructura exacta, sin texto adicional:\n"
        '{"ingredients": [{"name": "nombre del ingrediente", "confidence": 0.9}], "low_confidence": false}\n'
        "low_confidence debe ser true si la imagen es difícil de analizar o los ingredientes son inciertos."
    )

    message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{image_b64}"},
            },
            {"type": "text", "text": prompt},
        ]
    )

    response = llm.invoke([message])
    text = response.content if isinstance(response.content, str) else str(response.content)

    # Extract JSON object from response (model may include extra text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"ingredients": [], "low_confidence": True}

    try:
        data = json.loads(match.group())
        ingredients = [
            {
                "name": str(item.get("name", "")),
                "confidence": float(item.get("confidence", 0.0)),
            }
            for item in data.get("ingredients", [])
        ]
        return {
            "ingredients": ingredients,
            "low_confidence": bool(data.get("low_confidence", False)),
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {"ingredients": [], "low_confidence": True}
