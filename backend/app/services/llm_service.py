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
# Helper: Detect Permanent Errors
# ==========================================

def _is_permanent_error(
    error_text: str
) -> bool:
    """
    Detect errors that will not be fixed
    by retrying the same request.
    """

    return (
        "api key" in error_text
        or "authentication" in error_text
        or "permission" in error_text
        or "invalid argument" in error_text
        or "invalid api key" in error_text
        or "not found" in error_text
    )


# ==========================================
# Helper: Detect Daily / Project Quota
# ==========================================

def _is_quota_exhausted(
    error_text: str
) -> bool:
    """
    Detect hard quota exhaustion.

    Example:

    GenerateRequestsPerDayPerProjectPerModel-FreeTier

    This should NOT be retried because waiting
    a few seconds will not restore a daily quota.
    """

    return (
        "generate_requests_per_day" in error_text
        or "perdayperproject" in error_text
        or "daily quota" in error_text
        or "quota exceeded for metric" in error_text
        or "free_tier_requests" in error_text
    )


# ==========================================
# Helper: Detect Temporary Rate Limit
# ==========================================

def _is_rate_limit_error(
    error_text: str
) -> bool:
    """
    Detect temporary rate-limit conditions.

    These may succeed after waiting.
    """

    return (
        "429" in error_text
        or "too many requests" in error_text
        or "rate limit" in error_text
        or "ratelimit" in error_text
    )


# ==========================================
# Helper: Detect Retryable Errors
# ==========================================

def _is_retryable_error(
    error_text: str
) -> bool:
    """
    Detect temporary infrastructure/network
    failures that can reasonably be retried.
    """

    return (
        "timeout" in error_text
        or "timed out" in error_text
        or "connection reset" in error_text
        or "connection refused" in error_text
        or "temporary failure" in error_text
        or "temporarily unavailable" in error_text
        or "internal server error" in error_text
        or "service unavailable" in error_text
        or "bad gateway" in error_text
        or "gateway timeout" in error_text
        or "503" in error_text
        or "502" in error_text
        or "500" in error_text
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

            logger.info(
                "LLM ATTEMPT | "
                "attempt=%s/%s | model=%s",
                attempt + 1,
                LLM_MAX_RETRIES + 1,
                GEMINI_MODEL
            )

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

            error_text = str(
                e
            ).lower()

            logger.error(
                "LLM ERROR | "
                "attempt=%s | "
                "latency=%.2f seconds | %s",
                attempt + 1,
                latency,
                e
            )

            # ==========================================
            # 1. HARD QUOTA EXHAUSTION
            # ==========================================
            #
            # Example:
            #
            # GenerateRequestsPerDayPerProjectPerModel-FreeTier
            #
            # Do NOT retry.
            # ==========================================

            if _is_quota_exhausted(
                error_text
            ):

                logger.error(
                    "LLM QUOTA EXHAUSTED | "
                    "model=%s | "
                    "No retry will be attempted.",
                    GEMINI_MODEL
                )

                raise

            # ==========================================
            # 2. PERMANENT ERROR
            # ==========================================

            if _is_permanent_error(
                error_text
            ):

                logger.error(
                    "LLM PERMANENT ERROR | "
                    "model=%s | "
                    "No retry will be attempted.",
                    GEMINI_MODEL
                )

                raise

            # ==========================================
            # 3. MAXIMUM RETRIES
            # ==========================================

            if attempt >= LLM_MAX_RETRIES:

                logger.error(
                    "LLM FAILED | "
                    "Maximum retries reached | "
                    "attempts=%s",
                    LLM_MAX_RETRIES + 1
                )

                raise

            # ==========================================
            # 4. DETERMINE WHETHER RETRY IS USEFUL
            # ==========================================

            rate_limit_error = (
                _is_rate_limit_error(
                    error_text
                )
            )

            retryable_error = (
                _is_retryable_error(
                    error_text
                )
            )

            # ------------------------------------------
            # Retry temporary errors
            # ------------------------------------------

            if (
                rate_limit_error
                or retryable_error
            ):

                backoff_time = (
                    LLM_INITIAL_BACKOFF
                    * (2 ** attempt)
                )

                logger.warning(
                    "LLM RETRY | "
                    "retry=%s | "
                    "reason=%s | "
                    "waiting=%.2f seconds",
                    attempt + 1,
                    (
                        "rate_limit"
                        if rate_limit_error
                        else "transient_error"
                    ),
                    backoff_time
                )

                time.sleep(
                    backoff_time
                )

                continue

            # ==========================================
            # 5. UNKNOWN ERROR
            # ==========================================
            #
            # Unknown errors are treated as retryable
            # because they may be temporary.
            # ==========================================

            backoff_time = (
                LLM_INITIAL_BACKOFF
                * (2 ** attempt)
            )

            logger.warning(
                "LLM RETRY | "
                "retry=%s | "
                "reason=unknown_error | "
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