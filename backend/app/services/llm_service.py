import logging
import os
import time
import re

from dotenv import load_dotenv

from google import genai
from google.genai import types

from app.services.trace_service import (
    trace_log
)


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

LLM_INPUT_COST_PER_1M = float(
    os.getenv(
        "LLM_INPUT_COST_PER_1M",
        "0.30"
    )
)

LLM_OUTPUT_COST_PER_1M = float(
    os.getenv(
        "LLM_OUTPUT_COST_PER_1M",
        "2.50"
    )
)


# ==========================================
# Logging
# ==========================================

logger = logging.getLogger(__name__)


# ==========================================
# Central LLM Service
# ==========================================

class LLMService:
    """
    Central abstraction for LLM operations.

    Currently uses Gemini.

    Responsibilities:
    - Gemini client management
    - Model configuration
    - Text generation
    - Structured JSON output
    - Context-based answers
    - Retry handling
    - Quota handling
    - Temporary failure handling
    - Latency tracking
    - Token usage tracking
    - Cost estimation
    - Trace correlation
    - Operation-level observability
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None
    ):

        self.api_key = (
            api_key
            or GEMINI_API_KEY
        )

        self.model = (
            model
            or GEMINI_MODEL
        )

        self.temperature = (
            LLM_TEMPERATURE
        )

        self.max_tokens = (
            LLM_MAX_TOKENS
        )

        self.max_retries = (
            LLM_MAX_RETRIES
        )

        self.initial_backoff = (
            LLM_INITIAL_BACKOFF
        )

        # Cost configuration
        self.input_cost_per_1m = (
            LLM_INPUT_COST_PER_1M
        )

        self.output_cost_per_1m = (
            LLM_OUTPUT_COST_PER_1M
        )

        if not self.api_key:

            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        logger.info(
            "LLM SERVICE INITIALIZED | "
            "provider=gemini | model=%s",
            self.model
        )

        trace_log(
            "LLM_SERVICE_INITIALIZED",
            (
                f"provider=gemini "
                f"model={self.model}"
            )
        )

    # ==========================================
    # Token Usage + Cost Estimation
    # ==========================================

    def _log_token_usage(
        self,
        response
    ):

        usage = getattr(
            response,
            "usage_metadata",
            None
        )

        if usage:

            input_tokens = getattr(
                usage,
                "prompt_token_count",
                None
            )

            output_tokens = getattr(
                usage,
                "candidates_token_count",
                None
            )

            thinking_tokens = getattr(
                usage,
                "thoughts_token_count",
                0
            ) or 0

            total_tokens = getattr(
                usage,
                "total_token_count",
                None
            )

            input_cost = 0.0
            output_cost = 0.0

            # Input token cost
            if input_tokens is not None:

                input_cost = (
                    input_tokens
                    * self.input_cost_per_1m
                    / 1_000_000
                )

            # Output + thinking token cost
            if output_tokens is not None:

                billable_output_tokens = (
                    output_tokens
                    + thinking_tokens
                )

                output_cost = (
                    billable_output_tokens
                    * self.output_cost_per_1m
                    / 1_000_000
                )

            estimated_cost = (
                input_cost
                + output_cost
            )

            logger.info(
                "LLM USAGE | "
                "input_tokens=%s "
                "output_tokens=%s "
                "thinking_tokens=%s "
                "total_tokens=%s "
                "estimated_cost_usd=%.8f",

                input_tokens,

                output_tokens,

                thinking_tokens,

                total_tokens,

                estimated_cost
            )

            trace_log(
                "LLM_USAGE",
                (
                    f"input_tokens={input_tokens} "
                    f"output_tokens={output_tokens} "
                    f"thinking_tokens={thinking_tokens} "
                    f"total_tokens={total_tokens} "
                    f"estimated_cost_usd="
                    f"{estimated_cost:.8f}"
                )
            )

        else:

            logger.info(
                "LLM USAGE | "
                "token metadata unavailable"
            )

            trace_log(
                "LLM_USAGE",
                "token_metadata=unavailable"
            )

    # ==========================================
    # Permanent Error Detection
    # ==========================================

    def _is_permanent_error(
        self,
        error_text: str
    ) -> bool:

        return (

            "api key" in error_text

            or
            "authentication" in error_text

            or
            "permission" in error_text

            or
            "invalid argument" in error_text

            or
            "invalid api key" in error_text

            or
            "not found" in error_text
        )

    # ==========================================
    # Daily / Project Quota Detection
    # ==========================================

    def _is_quota_exhausted(
        self,
        error_text: str
    ) -> bool:

        return (

            "generate_requests_per_day"
            in error_text

            or
            "perdayperproject"
            in error_text

            or
            "daily quota"
            in error_text

            or
            "quota exceeded for metric"
            in error_text

            or
            "free_tier_requests"
            in error_text
        )

    # ==========================================
    # Rate Limit Detection
    # ==========================================

    def _is_rate_limit_error(
        self,
        error_text: str
    ) -> bool:

        return (

            "429" in error_text

            or
            "too many requests"
            in error_text

            or
            "rate limit"
            in error_text

            or
            "ratelimit"
            in error_text
        )

    # ==========================================
    # Retryable Error Detection
    # ==========================================

    def _is_retryable_error(
        self,
        error_text: str
    ) -> bool:

        return (

            "timeout" in error_text

            or
            "timed out" in error_text

            or
            "connection reset"
            in error_text

            or
            "connection refused"
            in error_text

            or
            "temporary failure"
            in error_text

            or
            "temporarily unavailable"
            in error_text

            or
            "internal server error"
            in error_text

            or
            "service unavailable"
            in error_text

            or
            "bad gateway"
            in error_text

            or
            "gateway timeout"
            in error_text

            or
            "503" in error_text

            or
            "502" in error_text

            or
            "500" in error_text
        )

    # ==========================================
    # Server Retry Delay
    # ==========================================

    def _get_retry_delay(
        self,
        error_text: str,
        attempt: int
    ) -> float:

        match = re.search(
            r"retryDelay['\"]?\s*[:=]\s*['\"]?(\d+)s",
            error_text,
            re.IGNORECASE
        )

        if match:

            return float(
                match.group(1)
            )

        match = re.search(
            r"retry in\s+(\d+(?:\.\d+)?)s",
            error_text,
            re.IGNORECASE
        )

        if match:

            return float(
                match.group(1)
            )

        return (
            self.initial_backoff
            *
            (
                2 ** attempt
            )
        )

    # ==========================================
    # Gemini Request With Retry
    # ==========================================

    def _generate_with_retry(
        self,
        contents: str,
        system_instruction: str,
        response_schema=None,
        operation_name: str = "unknown"
    ):

        total_attempts = (
            self.max_retries + 1
        )

        for attempt in range(
            total_attempts
        ):

            start_time = (
                time.perf_counter()
            )

            try:

                logger.info(
                    "LLM ATTEMPT | "
                    "provider=gemini | "
                    "operation=%s | "
                    "attempt=%s/%s | "
                    "model=%s | "
                    "structured_output=%s",

                    operation_name,

                    attempt + 1,

                    total_attempts,

                    self.model,

                    response_schema is not None
                )

                trace_log(
                    "LLM_REQUEST",
                    (
                        "provider=gemini "
                        f"model={self.model} "
                        f"operation={operation_name} "
                        f"attempt={attempt + 1}/"
                        f"{total_attempts} "
                        f"structured_output="
                        f"{response_schema is not None}"
                    )
                )

                config_kwargs = {

                    "system_instruction":
                        system_instruction,

                    "temperature":
                        self.temperature,

                    "max_output_tokens":
                        self.max_tokens
                }

                if response_schema is not None:

                    config_kwargs[
                        "response_mime_type"
                    ] = "application/json"

                    config_kwargs[
                        "response_schema"
                    ] = response_schema

                response = (
                    self.client
                    .models
                    .generate_content(

                        model=self.model,

                        contents=contents,

                        config=(
                            types
                            .GenerateContentConfig(
                                **config_kwargs
                            )
                        )
                    )
                )

                # ------------------------------
                # Token Usage + Cost
                # ------------------------------

                self._log_token_usage(
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
                    "LLM LATENCY | "
                    "operation=%s | "
                    "%.2f seconds",

                    operation_name,

                    latency
                )

                logger.info(
                    "LLM SUCCESS | "
                    "operation=%s | "
                    "attempt=%s",

                    operation_name,

                    attempt + 1
                )

                trace_log(
                    "LLM_SUCCESS",
                    (
                        f"model={self.model} "
                        f"operation={operation_name} "
                        f"attempt={attempt + 1} "
                        f"latency={latency:.2f}s"
                    )
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
                    "operation=%s | "
                    "attempt=%s | "
                    "latency=%.2f seconds | %s",

                    operation_name,

                    attempt + 1,

                    latency,

                    e
                )

                trace_log(
                    "LLM_ERROR",
                    (
                        f"model={self.model} "
                        f"operation={operation_name} "
                        f"attempt={attempt + 1} "
                        f"latency={latency:.2f}s "
                        f"error={e}"
                    ),
                    logging.ERROR
                )

                # ==========================================
                # HARD QUOTA
                # ==========================================

                if self._is_quota_exhausted(
                    error_text
                ):

                    logger.error(
                        "LLM QUOTA EXHAUSTED | "
                        "model=%s | "
                        "operation=%s | "
                        "No retry will be attempted.",

                        self.model,

                        operation_name
                    )

                    trace_log(
                        "LLM_QUOTA_EXHAUSTED",
                        (
                            f"model={self.model} "
                            f"operation={operation_name}"
                        ),
                        logging.ERROR
                    )

                    raise

                # ==========================================
                # PERMANENT ERROR
                # ==========================================

                if self._is_permanent_error(
                    error_text
                ):

                    logger.error(
                        "LLM PERMANENT ERROR | "
                        "model=%s | "
                        "operation=%s | "
                        "No retry will be attempted.",

                        self.model,

                        operation_name
                    )

                    trace_log(
                        "LLM_PERMANENT_ERROR",
                        (
                            f"model={self.model} "
                            f"operation={operation_name}"
                        ),
                        logging.ERROR
                    )

                    raise

                # ==========================================
                # MAXIMUM RETRIES
                # ==========================================

                if attempt >= self.max_retries:

                    logger.error(
                        "LLM FAILED | "
                        "Maximum retries reached | "
                        "operation=%s | "
                        "attempts=%s",

                        operation_name,

                        total_attempts
                    )

                    trace_log(
                        "LLM_RETRY_EXHAUSTED",
                        (
                            f"operation={operation_name} "
                            f"attempts={total_attempts}"
                        ),
                        logging.ERROR
                    )

                    raise

                # ==========================================
                # ERROR TYPE
                # ==========================================

                rate_limit_error = (
                    self._is_rate_limit_error(
                        error_text
                    )
                )

                retryable_error = (
                    self._is_retryable_error(
                        error_text
                    )
                )

                # ==========================================
                # TEMPORARY ERROR
                # ==========================================

                if (
                    rate_limit_error
                    or retryable_error
                ):

                    backoff_time = (
                        self._get_retry_delay(
                            error_text,
                            attempt
                        )
                    )

                    reason = (
                        "rate_limit"
                        if rate_limit_error
                        else "transient_error"
                    )

                    logger.warning(
                        "LLM RETRY | "
                        "provider=gemini | "
                        "operation=%s | "
                        "retry=%s | "
                        "reason=%s | "
                        "waiting=%.2f seconds",

                        operation_name,

                        attempt + 1,

                        reason,

                        backoff_time
                    )

                    trace_log(
                        "LLM_RETRY",
                        (
                            f"retry={attempt + 1} "
                            f"operation={operation_name} "
                            f"reason={reason} "
                            f"waiting={backoff_time:.2f}s"
                        ),
                        logging.WARNING
                    )

                    time.sleep(
                        backoff_time
                    )

                    continue

                # ==========================================
                # UNKNOWN ERROR
                # ==========================================

                backoff_time = (
                    self._get_retry_delay(
                        error_text,
                        attempt
                    )
                )

                logger.warning(
                    "LLM RETRY | "
                    "provider=gemini | "
                    "operation=%s | "
                    "retry=%s | "
                    "reason=unknown_error | "
                    "waiting=%.2f seconds",

                    operation_name,

                    attempt + 1,

                    backoff_time
                )

                trace_log(
                    "LLM_RETRY",
                    (
                        f"retry={attempt + 1} "
                        f"operation={operation_name} "
                        "reason=unknown_error "
                        f"waiting={backoff_time:.2f}s"
                    ),
                    logging.WARNING
                )

                time.sleep(
                    backoff_time
                )

    # ==========================================
    # Generate Answer
    # ==========================================

    def generate_answer(
        self,
        question: str,
        context: str
    ):

        user_prompt = f"""
Context:
{context}

Question:
{question}
"""

        response = (
            self._generate_with_retry(

                contents=user_prompt,

                system_instruction=(
                    "You are an operations analyst. "
                    "Answer the question using only "
                    "the provided context."
                ),

                operation_name="answer_generation"
            )
        )

        return response.text

    # ==========================================
    # Generate Text
    # ==========================================

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema=None,
        operation_name: str = "text_generation"
    ):

        response = (
            self._generate_with_retry(

                contents=user_prompt,

                system_instruction=(
                    system_prompt
                ),

                response_schema=(
                    response_schema
                ),

                operation_name=(
                    operation_name
                )
            )
        )

        return response.text


# ==========================================
# Backward-Compatible Helper Functions
# ==========================================

def generate_answer(
    question: str,
    context: str
):

    service = LLMService()

    return service.generate_answer(
        question,
        context
    )


def generate_text(
    system_prompt: str,
    user_prompt: str,
    response_schema=None,
    operation_name: str = "text_generation"
):

    service = LLMService()

    return service.generate_text(
        system_prompt,
        user_prompt,
        response_schema,
        operation_name
    )