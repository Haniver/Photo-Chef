import os

from langchain_tavily import TavilySearch


def search_recipes(ingredients: list[str]) -> list[dict]:
    """Search for recipes using the given ingredients.

    Args:
        ingredients: List of ingredient names.

    Returns:
        List of search result dicts with 'url', 'content', and optional 'title'.
    """
    query = "recipes with " + ", ".join(ingredients)
    tool = TavilySearch(
        max_results=3,
        tavily_api_key=os.environ.get("TAVILY_API_KEY"),
    )
    response = tool.invoke(query)
    return response.get("results", [])
