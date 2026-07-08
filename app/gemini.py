import os
import google.generativeai as genai
from dotenv import load_dotenv
import markdown

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API KEY =", api_key)
print("LAST 6 =", api_key[-6:] if api_key else "None")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


def ask_gemini(question):
    try:
        response = model.generate_content(question)
        text = response.text

        return markdown.markdown(
            text,
            extensions=["fenced_code", "tables"]
        )

    except Exception as e:
        return f"<h3>Error:</h3><pre>{str(e)}</pre>"