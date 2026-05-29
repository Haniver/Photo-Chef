from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


import os as _os

if _os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
