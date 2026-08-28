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
                user_prompt
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

            return IntentResult(
                intent=IntentType(
                    data.get(
                        "intent",
                        "unknown"
                    )
                ),
                confidence=float(
                    data.get(
                        "confidence",
                        0.0
                    )
                ),
                reasoning=data.get(
                    "reasoning"
                )
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