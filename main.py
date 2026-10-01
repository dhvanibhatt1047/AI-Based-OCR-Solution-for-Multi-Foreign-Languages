from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from pipeline import process_image, translate_text

app = FastAPI()

# Allow requests from any origin (your GUI on another PC included)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/translate")
async def translate_image(file: UploadFile = File(...)):
    # Save the uploaded image temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = process_image(temp_path)
    finally:
        os.remove(temp_path)  # clean up

    return result

from pydantic import BaseModel
from pipeline import translate_text

class TextRequest(BaseModel):
    text: str
    direction: str = "Chinese → English"

from pipeline import process_image, translate_text, detect_language

@app.post("/translate-text")
async def translate_text_only(request: TextRequest):
    if request.direction == "Auto detect":
        direction = detect_language(request.text)
    elif request.direction == "English → Chinese":
        direction = "en-zh"
    else:
        direction = "zh-en"

    translated = translate_text(request.text, direction=direction)
    return {
        "chinese_text": request.text,
        "english_text": translated,
        "accuracy": 100.0,
        "confidence": 100.0
    }
    