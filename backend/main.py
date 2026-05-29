import base64
import json

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from backend.agent import _ThinkStreamFilter, build_agent
from backend.agent_tools import make_analyze_image_tool
from backend.recipe import synthesize_recipe
from backend.search import search_recipes
from backend.vision import analyze_image, validate_image_format

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class AnalyzeImageRequest(BaseModel):
    image: str  # base64-encoded image, no data URI prefix


class Ingredient(BaseModel):
    name: str
    confidence: float


class AnalyzeImageResponse(BaseModel):
    ingredients: list[Ingredient]
    low_confidence: bool


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/analyze-image", response_model=AnalyzeImageResponse)
def analyze_image_endpoint(request: AnalyzeImageRequest):
    try:
        validate_image_format(request.image)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = analyze_image(request.image)
    return AnalyzeImageResponse(
        ingredients=[Ingredient(**i) for i in result["ingredients"]],
        low_confidence=result["low_confidence"],
    )


class RecipeRequest(BaseModel):
    ingredients: list[Ingredient]


class RecipeResponse(BaseModel):
    recipe: str


@app.post("/recipe", response_model=RecipeResponse)
async def recipe_endpoint(request: RecipeRequest):
    if not request.ingredients:
        raise HTTPException(status_code=422, detail="La lista de ingredientes no puede estar vacía.")

    names = [i.name for i in request.ingredients]
    low_confidence_items = [i.name for i in request.ingredients if i.confidence < 0.5]

    try:
        search_results = search_recipes(names)
        recipe_md = synthesize_recipe(names, search_results)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al generar la receta: {e}")

    if low_confidence_items:
        warning = (
            f"\n\n⚠️ Algunos ingredientes se detectaron con baja confianza: "
            f"{', '.join(low_confidence_items)}. "
            "Verifica que estén realmente disponibles antes de cocinar."
        )
        recipe_md = recipe_md + warning

    return RecipeResponse(recipe=recipe_md)


# ---------------------------------------------------------------------------
# SSE helper
# ---------------------------------------------------------------------------


def _sse(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# POST /chat — LangGraph agent with SSE streaming
# ---------------------------------------------------------------------------


@app.post("/chat")
async def chat_endpoint(
    image: UploadFile = File(...),
    message: str = Form(default=""),
    session_id: str = Form(default=""),
):
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode()

    try:
        validate_image_format(image_b64)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    analyze_tool = make_analyze_image_tool(image_b64)
    agent = build_agent(analyze_tool)

    user_text = message.strip()
    if user_text:
        human_content = f"Analiza mi refrigerador y sugiere una receta. {user_text}"
    else:
        human_content = "Analiza mi refrigerador y sugiere una receta."

    inputs = {"messages": [HumanMessage(content=human_content)]}
    config = {"configurable": {"thread_id": session_id or "default"}}

    async def generate():
        think_filter = _ThinkStreamFilter()
        seen_search = False
        emitted_synthesis = False

        try:
            async for event in agent.astream_events(inputs, version="v2", config=config):
                event_type: str = event.get("event", "")
                event_name: str = event.get("name", "")

                if event_type == "on_tool_start":
                    if "analyze_image" in event_name:
                        yield _sse("status", {"message": "Analizando tu refrigerador…"})
                    elif "search_recipes" in event_name:
                        yield _sse("status", {"message": "Buscando recetas en internet…"})
                        seen_search = True

                elif event_type == "on_chat_model_start" and seen_search and not emitted_synthesis:
                    yield _sse("status", {"message": "Preparando tu receta…"})
                    emitted_synthesis = True

                elif event_type == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk is None:
                        continue

                    # Skip reasoning/thinking chunks emitted via additional_kwargs
                    if getattr(chunk, "additional_kwargs", {}).get("reasoning_content"):
                        continue

                    content = chunk.content if isinstance(chunk.content, str) else ""
                    visible = think_filter.feed(content)
                    if visible:
                        yield _sse("token", {"text": visible})

            yield _sse("done", {})

        except Exception as exc:
            yield _sse("error", {"detail": str(exc)})

    return StreamingResponse(generate(), media_type="text/event-stream")


import os as _os

if _os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
