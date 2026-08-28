import os
from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

LLM_TEMPERATURE = float(
    os.getenv("LLM_TEMPERATURE", "0.2")
)

LLM_MAX_TOKENS = int(
    os.getenv("LLM_MAX_TOKENS", "1000")
)