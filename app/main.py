from fastapi import UploadFile, File
from pypdf import PdfReader
import io
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.gemini import ask_gemini


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


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

@app.get("/chat", response_class=HTMLResponse)
def chat(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html"
    )
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
async def summarize(request: Request, pdf: UploadFile = File(...)):
    pdf_reader = PdfReader(pdf.file)

    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    prompt = f"""
You are a PDF summarizer.

Summarize the following PDF in:
- 5 to 8 simple bullet points
- Easy English
- Highlight only important points
- Do not add any extra information

PDF Content:
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
@app.get("/quiz")
async def quiz_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="quiz.html"
    )
@app.post("/generate-quiz")
async def generate_quiz(request: Request, pdf: UploadFile = File(...)):
    pdf_reader = PdfReader(pdf.file)

    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    prompt = f"""
    Create 10 multiple choice questions (MCQs) from the following PDF.

    For each question:
    - Give 4 options (A, B, C, D)
    - Mention the correct answer
    - Keep the questions simple.

    {text[:10000]}
    """

    quiz = ask_gemini(prompt)

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "request": request,
            "quiz": quiz
        }
    )
@app.get("/notes")
async def notes_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="notes.html"
    )
@app.post("/generate-notes")
async def generate_notes(request: Request, text: str = Form(...)):

    prompt = f"""
    Convert the following text into clean, short study notes with bullet points:

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