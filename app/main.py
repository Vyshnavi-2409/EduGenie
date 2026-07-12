from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pypdf import PdfReader
from app.gemini import ask_gemini
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# ---------------- HOME ----------------

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "answer": ""
        }
    )


# ---------------- CHAT ----------------

@app.get("/chat", response_class=HTMLResponse)
def chat(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html"
    )


@app.post("/ask")
def ask(request: Request, question: str = Form(...)):
    answer = ask_gemini(question)

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "request": request,
            "question": question,
            "answer": answer
        }
    )


# ---------------- PDF SUMMARY ----------------

@app.get("/pdf", response_class=HTMLResponse)
async def pdf_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pdf.html",
        context={
            "request": request,
            "summary": None
        }
    )


@app.post("/summarize")
async def summarize(
    request: Request,
    pdf: UploadFile = File(...)
):

    pdf_reader = PdfReader(pdf.file)

    text = ""

    for page in pdf_reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    prompt = f"""
You are a PDF summarizer.

Summarize the following PDF.

Rules:
- 5 to 8 bullet points
- Easy English
- Highlight important points only

PDF:

{text[:10000]}
"""

    summary = ask_gemini(prompt)

    return templates.TemplateResponse(
        request=request,
        name="pdf.html",
        context={
            "request": request,
            "summary": summary
        }
    )
# ---------------- QUIZ ----------------

@app.get("/quiz")
async def quiz_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "request": request
        }
    )


@app.post("/generate-quiz")
async def generate_quiz(
    request: Request,
    topic: str = Form(...)
):

    prompt = f"""
Generate exactly 10 multiple choice questions on the topic "{topic}".

Rules:

1. Return ONLY valid JSON.
2. Do NOT use markdown.
3. Do NOT use ```json.
4. Do NOT use HTML tags.
5. Do NOT write explanations.
6. Generate exactly 10 questions.
7. Each question must have exactly 4 options.
8. Only ONE option is correct.
9. The answer must exactly match one option.

Return format:

[
  {{
    "question":"What is Python?",
    "options":[
      "Programming Language",
      "Database",
      "Browser",
      "Operating System"
    ],
    "answer":"Programming Language"
  }}
]
"""

    response = ask_gemini(prompt)

    if "429" in response or "quota" in response.lower():
        return templates.TemplateResponse(
            request=request,
            name="quiz.html",
            context={
                "request":request,
                "error":"⚠️ Gemini API daily limit reached. Please try again after some time."
                }

            )

    try:
        response = response.strip()
        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.replace("<p>", "")
        response = response.replace("</p>", "")
        response = response.replace("<br>", "")
        response = response.replace("</br>", "")

        start = response.find("[")
        end = response.rfind("]") + 1

        response = response[start:end].strip()

        quiz = json.loads(response)

        for i, q in enumerate(quiz):
            q["id"] = i + 1

    except Exception:
        return templates.TemplateResponse(
            request=request,
            name="quiz.html",
            context={
                "request": request,
                "error": "Gemini returned invalid JSON.",
                "raw": response
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "request": request,
            "topic": topic,
            "quiz": quiz
        }
    )
# ---------------- NOTES ----------------

@app.get("/notes")
async def notes_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="notes.html"
    )


@app.post("/generate-notes")
async def generate_notes(
    request: Request,
    text: str = Form(...)
):

    prompt = f"""
Convert the following text into clean study notes.

Rules:
- Use bullet points.
- Use proper headings.
- Bold important word.
- Keep the notes short.
- Use easy English.
- Highlight important points only.

Text:

{text}
"""

    notes = ask_gemini(prompt)

    return templates.TemplateResponse(
        request=request,
        name="notes.html",
        context={
            "request": request,
            "notes": notes
        }
    )