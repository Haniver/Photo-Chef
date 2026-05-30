"""Photo-Chef LangGraph ReAct agent."""

import os
import re

from langchain_core.tools import tool
from langchain_qwq import ChatQwen
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

_memory = MemorySaver()

_SYSTEM_PROMPT = """\
Eres Photo-Chef, un asistente culinario experto.
Tu flujo de trabajo es siempre el siguiente:
1. Llama a `analyze_image_tool` para identificar los ingredientes en el refrigerador del usuario.
2. Usa los ingredientes detectados para llamar a `search_recipes_tool` y buscar recetas en internet.
3. Sintetiza la mejor receta a partir de los resultados y preséntala de forma clara.

Formato de la receta:
- Usa Markdown: ## para el título, ### para secciones (Ingredientes, Pasos).
- Usa listas con guiones para ingredientes y pasos numerados para la preparación.
- Incluye emojis relevantes (🍳, 🥘, 🌿, etc.) para hacer la receta más atractiva.
- Si los ingredientes se detectaron con baja confianza, incluye una advertencia al usuario.

Idioma de respuesta:
- Si el usuario no incluye texto en su mensaje, responde en español.
- Si el usuario incluye texto, responde en el mismo idioma que ese texto.

Mensajes de seguimiento:
- Si el historial ya contiene una receta, responde directamente las preguntas del
  usuario sin volver a analizar la imagen ni buscar recetas, a menos que el usuario
  pida explícitamente una nueva receta.
"""


def strip_thinking_tokens(text: str) -> str:
    """Remove <think>...</think> blocks from text.

    Handles complete blocks, nested/multiline content, and incomplete blocks
    at end of text without raising errors.
    """
    # Remove complete <think>...</think> blocks (including multiline, non-greedy)
    result = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Remove any remaining incomplete opening <think> block at end of text
    result = re.sub(r"<think>.*$", "", result, flags=re.DOTALL)
    return result


class _ThinkStreamFilter:
    """Stateful streaming filter that removes <think>...</think> blocks chunk by chunk."""

    _OPEN = "<think>"
    _CLOSE = "</think>"

    def __init__(self) -> None:
        self._in_think = False
        self._pending = ""  # Partial open-tag held at end of previous chunk

    def feed(self, text: str) -> str:
        """Process one streaming chunk and return the visible portion."""
        text = self._pending + text
        self._pending = ""
        output: list[str] = []

        while text:
            if self._in_think:
                end = text.find(self._CLOSE)
                if end == -1:
                    text = ""
                    break
                text = text[end + len(self._CLOSE):]
                self._in_think = False
            else:
                start = text.find(self._OPEN)
                if start == -1:
                    # Guard against a partial <think> tag split across chunk boundary
                    tail_len = min(len(self._OPEN) - 1, len(text))
                    suffix = text[-tail_len:] if tail_len > 0 else ""
                    if suffix and self._OPEN.startswith(suffix):
                        output.append(text[:-tail_len])
                        self._pending = suffix
                    else:
                        output.append(text)
                    text = ""
                    break
                else:
                    output.append(text[:start])
                    text = text[start + len(self._OPEN):]
                    self._in_think = True

        return "".join(output)


def build_agent(image_b64: str | None):
    """Build a ReAct agent for a single chat request.

    Args:
        image_b64: Base64-encoded refrigerator image for the first request,
                   or None for follow-up messages (no new image).

    Returns:
        Compiled LangGraph CompiledStateGraph.
    """
    from backend.agent_tools import make_analyze_image_tool, search_recipes_tool

    if image_b64 is not None:
        analyze_image_tool = make_analyze_image_tool(image_b64)
    else:
        @tool
        def analyze_image_tool() -> str:  # type: ignore[misc]
            """Analyze the user's refrigerator photo and return a comma-separated list of
            detected ingredients. Call this tool first, before searching for recipes."""
            return (
                "No se ha proporcionado imagen nueva. "
                "Usa el historial de conversación para responder."
            )

    llm = ChatQwen(
        model="qwen3.5-flash",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        enable_thinking=True,
        thinking_budget=200,
        streaming=True,
    )

    return create_react_agent(
        llm,
        tools=[analyze_image_tool, search_recipes_tool],
        prompt=_SYSTEM_PROMPT,
        checkpointer=_memory,
    )
