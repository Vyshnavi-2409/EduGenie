import os
import google.generativeai as genai
from dotenv import load_dotenv
import markdown

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


def ask_gemini(question):
    try:
        response = model.generate_content(question)

        text = response.text

        html = markdown.markdown(
            text,
            extensions=["fenced_code", "tables"]
        )

        return html

    except Exception as e:
        return f"<p>{str(e)}</p>"