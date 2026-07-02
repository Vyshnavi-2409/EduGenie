from fastapi import FastAPI, Request, Form
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
        name="index.html",
        context={
            "request": request,
            "answer": answer
        }
    )