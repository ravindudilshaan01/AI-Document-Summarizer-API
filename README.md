# AI Document Summarizer API

A FastAPI backend that uses **Google Gemini** to summarize documents and extract structured insights — key points, sentiment, topics, and reading time.

## Features

- `/summarize/text` — summarize raw text via JSON body
- `/summarize/file` — upload a `.txt`, `.md`, or `.csv` file
- `/health` — health check endpoint
- Auto-generated interactive docs at `/docs`
- Structured JSON responses with Pydantic validation
- CORS enabled for frontend integration

## Tech stack

- **FastAPI** — API framework
- **Google Gemini 1.5 Flash** — LLM for analysis
- **Pydantic v2** — request/response validation
- **Uvicorn** — ASGI server
- **Docker** — containerised deployment

## Setup

### 1. Clone and install

```bash
git clone https://github.com/yourusername/ai-summarizer-api
cd ai-summarizer-api
pip install -r requirements.txt
```

### 2. Set your Gemini API key

```bash
cp .env.example .env
# Edit .env and add your key from https://aistudio.google.com/app/apikey
export GEMINI_API_KEY=your_key_here
```

### 3. Run

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## API usage

### Summarize text

```bash
curl -X POST http://localhost:8000/summarize/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Paste your document text here...", "language": "English"}'
```

### Summarize a file

```bash
curl -X POST http://localhost:8000/summarize/file \
  -F "file=@document.txt" \
  -F "language=English"
```

### Example response

```json
{
  "summary": "This document discusses the impact of AI on modern software development...",
  "key_points": [
    "AI tools reduce development time by up to 40%",
    "Code review automation is gaining adoption",
    "Junior developers benefit most from AI pair programming"
  ],
  "sentiment": "positive",
  "word_count": 842,
  "reading_time_minutes": 4.2,
  "topics": ["AI", "software development", "productivity", "code review"]
}
```

## Docker

```bash
docker build -t ai-summarizer-api .
docker run -e GEMINI_API_KEY=your_key -p 8000:8000 ai-summarizer-api
```

## Project structure

```
ai-summarizer-api/
├── app/
│   └── main.py          # All routes, models, and Gemini integration
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```
