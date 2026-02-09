from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import os
import json
import re

app = FastAPI(
    title="AI Document Summarizer API",
    description="Upload a document or paste text to get an AI-powered summary using Google Gemini.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


class TextInput(BaseModel):
    text: str
    language: Optional[str] = "English"


class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
    sentiment: str
    word_count: int
    reading_time_minutes: float
    topics: list[str]


PROMPT_TEMPLATE = """
You are a professional document analyst. Analyze the following text and respond ONLY with valid JSON matching this exact schema:

{{
  "summary": "A concise 2-3 sentence summary of the document",
  "key_points": ["point 1", "point 2", "point 3", "up to 5 key points"],
  "sentiment": "positive | negative | neutral | mixed",
  "topics": ["topic1", "topic2", "up to 4 main topics"]
}}

Text to analyze:
\"\"\"
{text}
\"\"\"

Respond in {language}. Return ONLY the JSON object, no markdown, no explanation.
"""


def parse_gemini_response(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"```$", "", raw)
    return json.loads(raw.strip())


@app.get("/")
def root():
    return {"message": "AI Document Summarizer API", "docs": "/docs"}


@app.post("/summarize/text", response_model=SummaryResponse)
async def summarize_text(body: TextInput):
    if len(body.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Text must be at least 50 characters.")

    prompt = PROMPT_TEMPLATE.format(text=body.text[:8000], language=body.language)

    try:
        response = model.generate_content(prompt)
        parsed = parse_gemini_response(response.text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Gemini returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

    word_count = len(body.text.split())
    reading_time = round(word_count / 200, 1)

    return SummaryResponse(
        summary=parsed["summary"],
        key_points=parsed["key_points"],
        sentiment=parsed["sentiment"],
        word_count=word_count,
        reading_time_minutes=reading_time,
        topics=parsed.get("topics", [])
    )


@app.post("/summarize/file", response_model=SummaryResponse)
async def summarize_file(
    file: UploadFile = File(...),
    language: str = "English"
):
    allowed = {"text/plain", "text/markdown", "text/csv"}
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: .txt, .md, .csv"
        )

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding must be UTF-8.")

    return await summarize_text(TextInput(text=text, language=language))


@app.get("/health")
def health():
    return {"status": "ok", "model": "gemini-1.5-flash"}
