import json
import logging

from app.models.intent import (
    IntentResult,
    IntentType
)

from app.prompts.intent_detection import (
    SYSTEM_PROMPT,
    USER_PROMPT
)

from app.services.llm_service import (
    generate_text
)


logger = logging.getLogger(__name__)


# ==================================================
# Native Structured Output Schema
# ==================================================

INTENT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "analyze_workflow",
                "find_bottleneck",
                "explain_delay",
                "recommend_action",
                "retrieve_jira_issue",
                "unknown"
            ]
        },
        "confidence": {
            "type": "number"
        },
        "reasoning": {
            "type": "string"
        }
    },
    "required": [
        "intent",
        "confidence",
        "reasoning"
    ]
}


class IntentService:
    """
    Service responsible for identifying
    the user's goal from natural language.
    """

    def detect(
        self,
        question: str
    ) -> IntentResult:

        logger.info(
            "INTENT DETECTION STARTED"
        )

        user_prompt = USER_PROMPT.format(
            question=question
        )

        try:

            response_text = generate_text(
                SYSTEM_PROMPT,
                user_prompt,
                response_schema=(
                    INTENT_RESPONSE_SCHEMA
                )
            )

            result = self._parse_response(
                response_text
            )

            logger.info(
                "INTENT DETECTED | intent=%s confidence=%.2f",
                result.intent.value,
                result.confidence
            )

            return result

        except Exception as e:

            logger.error(
                "INTENT DETECTION FAILED | %s",
                e
            )

            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                reasoning=(
                    "Intent detection failed."
                )
            )

    # ==================================================
    # Parse Intent Response
    # ==================================================

    def _parse_response(
        self,
        response_text: str
    ) -> IntentResult:

        try:

            json_start = (
                response_text.find("{")
            )

            json_end = (
                response_text.rfind("}") + 1
            )

            if (
                json_start == -1
                or json_end <= json_start
            ):

                raise ValueError(
                    "No JSON object found."
                )

            json_str = (
                response_text[
                    json_start:json_end
                ]
            )

            data = json.loads(
                json_str
            )

            # ------------------------------------------
            # Validate Intent
            # ------------------------------------------

            intent = IntentType(
                data.get(
                    "intent",
                    "unknown"
                )
            )

            # ------------------------------------------
            # Validate Confidence
            # ------------------------------------------

            confidence = float(
                data.get(
                    "confidence",
                    0.0
                )
            )

            if not 0.0 <= confidence <= 1.0:

                raise ValueError(
                    "Confidence must be between "
                    "0.0 and 1.0."
                )

            # ------------------------------------------
            # Validate Reasoning
            # ------------------------------------------

            reasoning = data.get(
                "reasoning"
            )

            if reasoning is not None:

                reasoning = str(
                    reasoning
                ).strip()

            # ------------------------------------------
            # Build Validated Result
            # ------------------------------------------

            return IntentResult(
                intent=intent,
                confidence=confidence,
                reasoning=reasoning
            )

        except (
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):

            logger.warning(
                "Invalid intent response"
            )

            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                reasoning=(
                    "Unable to parse intent."
                )
            )


# ==================================================
# Convenience Function
# ==================================================

def detect_intent(
    question: str
) -> IntentResult:
    """
    Convenience function for intent detection.
    """

    service = IntentService()

    return service.detect(
        question
    )