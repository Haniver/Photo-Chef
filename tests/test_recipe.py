"""Tests for Fase 3 — Búsqueda de recetas."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Pre-import modules so patch() can resolve them in Python 3.13+
import backend.search  # noqa: F401
import backend.recipe  # noqa: F401
import backend.main    # noqa: F401

from backend.main import app
from backend.search import search_recipes
from backend.recipe import synthesize_recipe


# ---------------------------------------------------------------------------
# Unit tests — search_recipes
# ---------------------------------------------------------------------------


def test_search_recipes_builds_correct_query():
    """The query sent to Tavily must contain the ingredient names."""
    ingredients = ["tomate", "huevo", "queso"]
    captured_queries = []

    def fake_invoke(query):
        captured_queries.append(query)
        return {"results": [{"url": "http://example.com", "content": "recipe content"}]}

    with patch("backend.search.TavilySearch") as MockTavily:
        instance = MockTavily.return_value
        instance.invoke.side_effect = fake_invoke
        search_recipes(ingredients)

    assert len(captured_queries) == 1
    query = captured_queries[0]
    for ingredient in ingredients:
        assert ingredient in query


def test_search_recipes_returns_results():
    """With a mock returning 3 results, the function returns them without transformation."""
    fake_results = [
        {"url": "http://a.com", "content": "Recipe A", "title": "A"},
        {"url": "http://b.com", "content": "Recipe B", "title": "B"},
        {"url": "http://c.com", "content": "Recipe C", "title": "C"},
    ]

    with patch("backend.search.TavilySearch") as MockTavily:
        MockTavily.return_value.invoke.return_value = {"results": fake_results}
        results = search_recipes(["tomate", "huevo"])

    assert results == fake_results


# ---------------------------------------------------------------------------
# Unit tests — synthesize_recipe
# ---------------------------------------------------------------------------


def test_synthesize_recipe_calls_llm():
    """The LLM prompt must include the ingredients and the search results content."""
    ingredients = ["tomate", "huevo"]
    search_results = [{"url": "http://a.com", "content": "Tortilla española con tomate"}]

    captured_messages = []

    def fake_invoke(messages):
        captured_messages.extend(messages)
        mock_resp = MagicMock()
        mock_resp.content = "# Tortilla\n\n- Huevo\n\n1. Cocinar"
        return mock_resp

    with patch("backend.recipe.ChatQwen") as MockLLM:
        MockLLM.return_value.invoke.side_effect = fake_invoke
        synthesize_recipe(ingredients, search_results)

    combined = " ".join(str(m.content) for m in captured_messages)
    for ingredient in ingredients:
        assert ingredient in combined
    assert "Tortilla española con tomate" in combined


def test_synthesize_recipe_returns_markdown_string():
    """The function returns the LLM's string content directly."""
    expected = "# Receta de prueba\n\n- ingrediente\n\n1. paso"

    mock_resp = MagicMock()
    mock_resp.content = expected

    with patch("backend.recipe.ChatQwen") as MockLLM:
        MockLLM.return_value.invoke.return_value = mock_resp
        result = synthesize_recipe(["tomate"], [{"url": "http://x.com", "content": "x"}])

    assert result == expected


# ---------------------------------------------------------------------------
# Integration tests — POST /recipe endpoint
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_pipeline():
    """Patch both search_recipes and synthesize_recipe for endpoint tests."""
    with (
        patch("backend.main.search_recipes") as mock_search,
        patch("backend.main.synthesize_recipe") as mock_synth,
    ):
        mock_search.return_value = [{"url": "http://x.com", "content": "content"}]
        mock_synth.return_value = "# Receta\n\n- tomate\n\n1. Cocinar el tomate"
        yield mock_search, mock_synth


@pytest.mark.asyncio
async def test_recipe_endpoint_returns_200_with_ingredients(mock_pipeline):
    """POST /recipe with valid ingredients returns HTTP 200 and a recipe body."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/recipe",
            json={"ingredients": [{"name": "tomate", "confidence": 0.9}, {"name": "huevo", "confidence": 0.8}]},
        )

    assert response.status_code == 200
    data = response.json()
    assert "recipe" in data
    assert isinstance(data["recipe"], str)
    assert len(data["recipe"]) > 0


@pytest.mark.asyncio
async def test_recipe_endpoint_returns_422_with_empty_ingredients():
    """POST /recipe with an empty ingredients list returns HTTP 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/recipe", json={"ingredients": []})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_recipe_endpoint_warns_low_confidence_ingredients(mock_pipeline):
    """When any ingredient has confidence < 0.5, the recipe markdown contains ⚠️."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/recipe",
            json={
                "ingredients": [
                    {"name": "tomate", "confidence": 0.9},
                    {"name": "algo_raro", "confidence": 0.3},
                ]
            },
        )

    assert response.status_code == 200
    recipe_text = response.json()["recipe"]
    assert "⚠️" in recipe_text
    assert "algo_raro" in recipe_text


