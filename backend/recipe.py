import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_qwq import ChatQwen


_SYSTEM_PROMPT = (
    "Eres un chef experto. Tu tarea es:\n"
    "1. Leer los resultados de búsqueda proporcionados.\n"
    "2. Seleccionar la receta más adecuada para los ingredientes disponibles.\n"
    "3. Presentar la receta en Markdown bien estructurado:\n"
    "   - Título con # (nivel 1)\n"
    "   - Sección de ingredientes con lista de viñetas\n"
    "   - Pasos numerados\n"
    "4. Usar el idioma indicado (por defecto: español).\n"
    "Responde SOLO con el Markdown de la receta, sin texto adicional."
)


def synthesize_recipe(
    ingredients: list[str],
    search_results: list[dict],
    language: str = "español",
) -> str:
    """Synthesize a recipe from ingredients and search results.

    Args:
        ingredients: List of ingredient names.
        search_results: List of Tavily search result dicts.
        language: Language for the response (default: español).

    Returns:
        Markdown string of the synthesized recipe.
    """
    llm = ChatQwen(
        model="qwen3.5-flash",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        enable_thinking=True,
        thinking_budget=200,
    )

    results_text = "\n\n".join(
        f"Fuente: {r.get('url', '')}\n{r.get('content', '')}"
        for r in search_results
    )

    user_message = (
        f"Ingredientes disponibles: {', '.join(ingredients)}\n\n"
        f"Idioma de respuesta: {language}\n\n"
        f"Resultados de búsqueda:\n{results_text}"
    )

    response = llm.invoke(
        [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]
    )

    content = response.content if isinstance(response.content, str) else str(response.content)
    return content
