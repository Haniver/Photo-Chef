"""LangGraph tools for the Photo-Chef agent."""

from langchain_core.tools import tool

from backend.search import search_recipes
from backend.vision import analyze_image


def make_analyze_image_tool(image_b64: str):
    """Create a LangGraph tool that analyzes a refrigerator image provided in base64.

    Args:
        image_b64: Base64-encoded refrigerator image.

    Returns:
        A @tool that returns detected ingredients as a comma-separated string.
    """

    @tool
    def analyze_image_tool() -> str:
        """Analyze the user's refrigerator photo and return a comma-separated list of
        detected ingredients. Call this tool first, before searching for recipes."""
        result = analyze_image(image_b64)
        ingredients = [item["name"] for item in result.get("ingredients", [])]
        if not ingredients:
            return "No se detectaron ingredientes en la imagen."
        output = ", ".join(ingredients)
        if result.get("low_confidence"):
            output += " (nota: baja confianza en la detección de ingredientes)"
        return output

    return analyze_image_tool


@tool
def search_recipes_tool(ingredients: str) -> str:
    """Search the web for recipes using a comma-separated list of ingredients.
    Call this tool after identifying ingredients to find suitable recipes.

    Args:
        ingredients: Comma-separated list of ingredient names detected in the fridge.
    """
    ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]
    if not ingredient_list:
        return "No se proporcionaron ingredientes para buscar recetas."
    results = search_recipes(ingredient_list)
    if not results:
        return "No se encontraron recetas para estos ingredientes."
    return "\n\n".join(
        f"Fuente: {r.get('url', '')}\n{r.get('content', '')}"
        for r in results
    )
