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
    recommendations, and evaluating evidence
    using Gemini and retrieved RAG knowledge.
    """

    def __init__(self):

        self.context_service = (
            ContextService()
        )

    # ==================================================
    # SELF-CORRECTION
    # Evidence Evaluation
    # ==================================================

    def evaluate_evidence(
        self,
        insight: Insight,
        combined_evidence: dict | None = None
    ) -> dict:
        """
        Evaluate whether the available evidence
        is sufficient to support the insight.

        Gemini evaluates:

        1. Relevance
        2. Specificity
        3. Support
        4. Completeness

        Returns a structured evaluation.
        """

        combined_evidence = (
            combined_evidence
            or {}
        )

        jira_evidence = (
            combined_evidence.get(
                "jira",
                []
            )
        )

        slack_evidence = (
            combined_evidence.get(
                "slack",
                []
            )
        )

        insight_evidence = (
            insight.evidence
            or []
        )

        evaluator_prompt = f"""
Evaluate whether the available evidence is
sufficient to support the operational insight.

INSIGHT:
{insight.issue}

SEVERITY:
{insight.severity}

EXISTING INSIGHT EVIDENCE:
{json.dumps(insight_evidence, default=str)}

JIRA EVIDENCE:
{json.dumps(jira_evidence, default=str)}

SLACK EVIDENCE:
{json.dumps(slack_evidence, default=str)}

Evaluate the evidence using these criteria:

1. RELEVANCE
Does the evidence directly relate to the issue?

2. SPECIFICITY
Does the evidence contain concrete facts,
events, identifiers, timestamps, or measurable
information rather than vague statements?

3. SUPPORT
Does the evidence actually support the claim
made by the insight?

4. COMPLETENESS
Is there enough information to confidently
understand and support the issue?

Score each criterion from 0.0 to 1.0.

Use this interpretation:

0.0 = completely absent
0.25 = very weak
0.50 = partial
0.75 = strong
1.0 = very strong

Evidence should be considered sufficient only when
the evidence provides enough direct support for the
insight.

If evidence is insufficient, identify exactly what
information is missing.

Return ONLY valid JSON:

{{
    "sufficient": true,
    "relevance": 0.0,
    "specificity": 0.0,
    "support": 0.0,
    "completeness": 0.0,
    "reason": "Explain the decision.",
    "missing_information": []
}}
"""

        try:

            response_text = generate_text(
                (
                    "You are an evidence evaluation "
                    "agent for an operational "
                    "intelligence system. "
                    "Evaluate evidence objectively. "
                    "Do not invent facts. "
                    "Return only valid JSON."
                ),
                evaluator_prompt
            )

            evaluation = (
                self._parse_evaluation_response(
                    response_text
                )
            )

            logger.info(
                "EVIDENCE EVALUATION | "
                "sufficient=%s | "
                "relevance=%.2f | "
                "specificity=%.2f | "
                "support=%.2f | "
                "completeness=%.2f",
                evaluation["sufficient"],
                evaluation["relevance"],
                evaluation["specificity"],
                evaluation["support"],
                evaluation["completeness"]
            )

            if evaluation[
                "missing_information"
            ]:

                logger.info(
                    "MISSING EVIDENCE | %s",
                    evaluation[
                        "missing_information"
                    ]
                )

            return evaluation

        except Exception as e:

            logger.error(
                "EVIDENCE EVALUATION ERROR | %s",
                e
            )

            # ----------------------------------
            # Fail closed
            # ----------------------------------
            #
            # If evaluation itself fails,
            # do NOT assume evidence is sufficient.
            #

            return {
                "sufficient": False,
                "relevance": 0.0,
                "specificity": 0.0,
                "support": 0.0,
                "completeness": 0.0,
                "reason": (
                    "Evidence evaluation failed. "
                    "Additional evidence is required "
                    "before relying on this insight."
                ),
                "missing_information": [
                    "Reliable evidence evaluation"
                ]
            }

    # ==================================================
    # Parse Evidence Evaluation
    # ==================================================

    def _parse_evaluation_response(
        self,
        response_text: str
    ) -> dict:
        """
        Parse and validate Gemini's evidence
        evaluation response.
        """

        if not response_text:

            raise ValueError(
                "Empty evidence evaluation response."
            )

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
                    "Evidence evaluation "
                    "response is not JSON."
                )

            json_str = (
                response_text[
                    json_start:json_end
                ]
            )

            evaluation = json.loads(
                json_str
            )

            if not isinstance(
                evaluation,
                dict
            ):

                raise ValueError(
                    "Evidence evaluation "
                    "must be a JSON object."
                )

            # ----------------------------------
            # Sufficient
            # ----------------------------------

            sufficient = evaluation.get(
                "sufficient",
                False
            )

            if not isinstance(
                sufficient,
                bool
            ):

                sufficient = (
                    str(
                        sufficient
                    ).lower()
                    == "true"
                )

            # ----------------------------------
            # Numeric scores
            # ----------------------------------

            relevance = self._normalize_score(
                evaluation.get(
                    "relevance",
                    0.0
                )
            )

            specificity = self._normalize_score(
                evaluation.get(
                    "specificity",
                    0.0
                )
            )

            support = self._normalize_score(
                evaluation.get(
                    "support",
                    0.0
                )
            )

            completeness = self._normalize_score(
                evaluation.get(
                    "completeness",
                    0.0
                )
            )

            # ----------------------------------
            # Reason
            # ----------------------------------

            reason = evaluation.get(
                "reason",
                "No evaluation reason provided."
            )

            if not isinstance(
                reason,
                str
            ):

                reason = str(
                    reason
                )

            reason = reason.strip()

            # ----------------------------------
            # Missing information
            # ----------------------------------

            missing_information = (
                evaluation.get(
                    "missing_information",
                    []
                )
            )

            if not isinstance(
                missing_information,
                list
            ):

                missing_information = [
                    str(
                        missing_information
                    )
                ]

            missing_information = [
                str(item).strip()
                for item
                in missing_information
                if str(item).strip()
            ]

            return {
                "sufficient": sufficient,
                "relevance": relevance,
                "specificity": specificity,
                "support": support,
                "completeness": completeness,
                "reason": reason,
                "missing_information": (
                    missing_information
                )
            }

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError
        ) as e:

            logger.error(
                "EVIDENCE EVALUATION PARSE ERROR | %s",
                e
            )

            raise ValueError(
                "Invalid evidence evaluation response."
            )

    # ==================================================
    # Normalize Evaluation Score
    # ==================================================

    def _normalize_score(
        self,
        value
    ) -> float:
        """
        Convert a Gemini score into a safe
        float between 0.0 and 1.0.
        """

        try:

            score = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0

        return max(
            0.0,
            min(
                1.0,
                score
            )
        )

    # ==================================================
    # Generate Insight Analysis
    # ==================================================

    def generate_insight_analysis(
        self,
        insight: Insight,
        combined_evidence: dict | None = None,
        long_term_memory: list[str] | None = None
    ) -> Insight:
        """
        Generate root cause, impact, and recommendation
        using workflow evidence, Jira evidence,
        Slack evidence, retrieved RAG knowledge,
        and previous workflow execution memory.
        """

        user_prompt = self._build_prompt(
            insight,
            combined_evidence,
            long_term_memory
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

    # ==================================================
    # Build Prompt
    # ==================================================

    def _build_prompt(
        self,
        insight: Insight,
        combined_evidence: dict | None = None,
        long_term_memory: list[str] | None = None
    ) -> str:
        """
        Build the final prompt using operational
        evidence, retrieved RAG knowledge, and
        previous workflow execution memory.
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
        # Prepare combined context
        # --------------------------------

        context_state = {
            **(
                combined_evidence
                or {}
            ),
            "long_term_memory": (
                long_term_memory
                or []
            )
        }

        logger.info(
            "REASONING CONTEXT | "
            "long_term_memory=%s",
            len(
                long_term_memory
                or []
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
                agent_state=context_state
            )
        )

        return USER_PROMPT.format(
            context=context
        )

    # ==================================================
    # RAG Context
    # ==================================================

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

    # ==================================================
    # Parse Analysis Response
    # ==================================================

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

    # ==================================================
    # Validate Field
    # ==================================================

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


# ==================================================
# Convenience Function
# ==================================================

def generate_insight_analysis(
    insight: Insight,
    combined_evidence: dict | None = None,
    long_term_memory: list[str] | None = None
) -> Insight:
    """
    Convenience function to generate
    insight analysis.
    """

    service = GeminiInsightService()

    return service.generate_insight_analysis(
        insight,
        combined_evidence,
        long_term_memory
    )