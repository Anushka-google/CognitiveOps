import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# model = genai.GenerativeModel(
#     "gemini-2.0-flash"
# )
model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

def generate_answer(
    question: str,
    context: str
):
    prompt = f"""
You are an operations analyst.

Context:
{context}

Question:
{question}

Answer the question using only the provided context.
"""

    response = model.generate_content(prompt)

    return response.text