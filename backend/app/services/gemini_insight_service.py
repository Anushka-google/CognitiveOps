import json
import logging

from app.prompts.insight_analysis import (
    SYSTEM_PROMPT,
    USER_PROMPT
)

from app.models.insight import Insight

from app.services.llm_service import generate_text

from app.services.context_service import (
    ContextService
)

from app.services.vector_store import (
    get_context
)


logger = logging.getLogger(__name__)


class GeminiInsightService:
    """
    Service for generating root cause, impact,
    and recommendations using Gemini and
    retrieved RAG knowledge.
    """

    def __init__(self):

        self.context_service = (
            ContextService()
        )

    def generate_insight_analysis(
        self,
        insight: Insight,
        combined_evidence: dict | None = None
    ) -> Insight:
        """
        Generate root cause, impact, and recommendation
        using workflow evidence, Jira evidence,
        Slack evidence, and retrieved RAG knowledge.
        """

        user_prompt = self._build_prompt(
            insight,
            combined_evidence
        )

        response_text = generate_text(
            SYSTEM_PROMPT,
            user_prompt
        )

        analysis = self._parse_response(
            response_text
        )

        # --------------------------------
        # Validate Root Cause
        # --------------------------------

        root_cause = self._validate_field(
            analysis.get("root_cause"),
            "root_cause"
        )

        # --------------------------------
        # Validate Impact
        # --------------------------------

        impact = self._validate_field(
            analysis.get("impact"),
            "impact"
        )

        # --------------------------------
        # Validate Recommendation
        # --------------------------------

        recommendation = self._validate_field(
            analysis.get("recommendation"),
            "recommendation"
        )

        # --------------------------------
        # Validate Final Insight
        # --------------------------------

        validated_insight = Insight(
            issue=insight.issue,
            evidence=insight.evidence,
            severity=insight.severity,
            root_cause=root_cause,
            impact=impact,
            recommendation=recommendation
        )

        return validated_insight

    def _build_prompt(
        self,
        insight: Insight,
        combined_evidence: dict | None = None
    ) -> str:
        """
        Build the final prompt using operational
        evidence and retrieved RAG knowledge.
        """

        # --------------------------------
        # Retrieve relevant knowledge
        # --------------------------------

        retrieved_context = (
            self._get_rag_context(
                insight
            )
        )

        # --------------------------------
        # ContextService owns
        # complete context construction
        # --------------------------------

        context = (
            self.context_service
            .build_insight_context(
                insight=insight,
                retrieved_context=retrieved_context,
                agent_state=combined_evidence
            )
        )

        return USER_PROMPT.format(
            context=context
        )

    def _get_rag_context(
        self,
        insight: Insight
    ) -> str:
        """
        Retrieve relevant knowledge from ChromaDB.
        """

        query = (
            f"{insight.issue} "
            f"{insight.severity}"
        )

        try:

            context = get_context(
                query
            )

            if not context:

                return (
                    "No relevant knowledge "
                    "was found."
                )

            return context

        except Exception as e:

            logger.error(
                "RAG RETRIEVAL ERROR | %s",
                e
            )

            return (
                "No relevant knowledge "
                "was found."
            )

    def _parse_response(
        self,
        response_text: str
    ) -> dict:
        """
        Parse and validate the JSON response
        returned by Gemini.
        """

        if not response_text:

            logger.warning(
                "LLM RESPONSE EMPTY"
            )

            return {
                "root_cause": (
                    "Unable to determine root cause."
                ),
                "impact": (
                    "Unable to determine impact."
                ),
                "recommendation": (
                    "Please review manually."
                )
            }

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

                logger.warning(
                    "LLM RESPONSE IS NOT JSON"
                )

                return {
                    "root_cause": (
                        "Unable to determine root cause "
                        "from the available evidence."
                    ),
                    "impact": response_text,
                    "recommendation": (
                        "Please review manually."
                    )
                }

            json_str = (
                response_text[
                    json_start:json_end
                ]
            )

            parsed_data = json.loads(
                json_str
            )

            if not isinstance(
                parsed_data,
                dict
            ):

                logger.warning(
                    "LLM JSON RESPONSE "
                    "IS NOT AN OBJECT"
                )

                return {
                    "root_cause": (
                        "Unable to determine root cause "
                        "from the available evidence."
                    ),
                    "impact": response_text,
                    "recommendation": (
                        "Please review manually."
                    )
                }

            return parsed_data

        except json.JSONDecodeError as e:

            logger.warning(
                "LLM JSON PARSE ERROR | %s",
                e
            )

            return {
                "root_cause": (
                    "Unable to determine root cause "
                    "from the available evidence."
                ),
                "impact": response_text,
                "recommendation": (
                    "Please review manually."
                )
            }

    def _validate_field(
        self,
        value,
        field_name: str
    ) -> str:
        """
        Validate an individual LLM output field.
        """

        if value is None:

            logger.warning(
                "LLM FIELD MISSING | field=%s",
                field_name
            )

            if field_name == "root_cause":

                return (
                    "Unable to determine root cause "
                    "from the available evidence."
                )

            if field_name == "impact":

                return (
                    "Unable to determine impact."
                )

            return (
                "Please review manually."
            )

        if not isinstance(
            value,
            str
        ):

            logger.warning(
                "LLM FIELD INVALID TYPE | "
                "field=%s type=%s",
                field_name,
                type(value).__name__
            )

            return str(value)

        value = value.strip()

        if not value:

            logger.warning(
                "LLM FIELD EMPTY | field=%s",
                field_name
            )

            if field_name == "root_cause":

                return (
                    "Unable to determine root cause "
                    "from the available evidence."
                )

            if field_name == "impact":

                return (
                    "Unable to determine impact."
                )

            return (
                "Please review manually."
            )

        return value


def generate_insight_analysis(
    insight: Insight,
    combined_evidence: dict | None = None
) -> Insight:
    """
    Convenience function to generate
    insight analysis.
    """

    service = GeminiInsightService()

    return service.generate_insight_analysis(
        insight,
        combined_evidence
    )