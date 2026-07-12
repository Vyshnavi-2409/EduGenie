import os
from dotenv import load_dotenv
from google import genai
import markdown

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(api_key)
print(len(api_key) if api_key else "No Key")

client = genai.Client(api_key=api_key)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def ask_gemini(question):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        text = response.text

        html = markdown.markdown(
            text,
            extensions=["fenced_code", "tables"]
        )

        return html

    except Exception as e:
        return f"<p>{str(e)}</p>"