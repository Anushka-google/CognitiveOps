import os
import time
import logging

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# Environment Configuration
# ==========================================

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

LLM_TEMPERATURE = float(
    os.getenv(
        "LLM_TEMPERATURE",
        "0.2"
    )
)

LLM_MAX_TOKENS = int(
    os.getenv(
        "LLM_MAX_TOKENS",
        "1000"
    )
)

LLM_MAX_RETRIES = int(
    os.getenv(
        "LLM_MAX_RETRIES",
        "3"
    )
)

LLM_INITIAL_BACKOFF = float(
    os.getenv(
        "LLM_INITIAL_BACKOFF",
        "2"
    )
)


# ==========================================
# Logging
# ==========================================

logger = logging.getLogger(__name__)


# ==========================================
# Gemini Client
# ==========================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==========================================
# Helper: Log Token Usage
# ==========================================

def _log_token_usage(response):

    usage = getattr(
        response,
        "usage_metadata",
        None
    )

    if usage:

        logger.info(
            "LLM USAGE | input_tokens=%s "
            "output_tokens=%s "
            "total_tokens=%s",
            getattr(
                usage,
                "prompt_token_count",
                None
            ),
            getattr(
                usage,
                "candidates_token_count",
                None
            ),
            getattr(
                usage,
                "total_token_count",
                None
            )
        )

    else:

        logger.info(
            "LLM USAGE | token metadata unavailable"
        )


# ==========================================
# Helper: Gemini Request With Retry
# ==========================================

def _generate_with_retry(
    contents: str,
    system_instruction: str
):

    for attempt in range(
        LLM_MAX_RETRIES + 1
    ):

        start_time = time.perf_counter()

        try:

            response = (
                client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            system_instruction
                        ),
                        temperature=(
                            LLM_TEMPERATURE
                        ),
                        max_output_tokens=(
                            LLM_MAX_TOKENS
                        )
                    )
                )
            )

            # ------------------------------
            # Token Usage
            # ------------------------------

            _log_token_usage(
                response
            )

            # ------------------------------
            # Latency
            # ------------------------------

            latency = (
                time.perf_counter()
                - start_time
            )

            logger.info(
                "LLM LATENCY | %.2f seconds",
                latency
            )

            logger.info(
                "LLM SUCCESS | attempt=%s",
                attempt + 1
            )

            return response

        except Exception as e:

            latency = (
                time.perf_counter()
                - start_time
            )

            logger.error(
                "LLM ERROR | attempt=%s "
                "latency=%.2f seconds | %s",
                attempt + 1,
                latency,
                e
            )

            error_text = str(e).lower()

            # ------------------------------
            # Do not retry permanent errors
            # ------------------------------

            permanent_error = (
                "api key" in error_text
                or "authentication" in error_text
                or "permission" in error_text
                or "invalid argument" in error_text
                or "not found" in error_text
            )

            if permanent_error:

                logger.error(
                    "LLM PERMANENT ERROR | "
                    "Retry will not be attempted."
                )

                raise

            # ------------------------------
            # Maximum retries reached
            # ------------------------------

            if attempt >= LLM_MAX_RETRIES:

                logger.error(
                    "LLM FAILED | Maximum retries reached."
                )

                raise

            # ------------------------------
            # Exponential Backoff
            # ------------------------------

            backoff_time = (
                LLM_INITIAL_BACKOFF
                * (2 ** attempt)
            )

            logger.warning(
                "LLM RETRY | retry=%s "
                "waiting=%.2f seconds",
                attempt + 1,
                backoff_time
            )

            time.sleep(
                backoff_time
            )


# ==========================================
# Generate Answer
# ==========================================

def generate_answer(
    question: str,
    context: str
):
    """
    Generate an answer using the provided context.
    """

    user_prompt = f"""
Context:
{context}

Question:
{question}
"""

    response = _generate_with_retry(
        contents=user_prompt,
        system_instruction=(
            "You are an operations analyst. "
            "Answer the question using only "
            "the provided context."
        )
    )

    return response.text


# ==========================================
# Generate Text
# ==========================================

def generate_text(
    system_prompt: str,
    user_prompt: str
):
    """
    Generate text using separate
    system and user prompts.
    """

    response = _generate_with_retry(
        contents=user_prompt,
        system_instruction=system_prompt
    )

    return response.text