from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
