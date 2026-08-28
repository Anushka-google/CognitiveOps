import logging
import time

from app.agents.state import AgentState

from app.services.gemini_insight_service import (
    GeminiInsightService
)

from app.services.recommendation_service import (
    RecommendationService
)


logger = logging.getLogger(__name__)


def reasoning_agent(
    state: AgentState
):

    logger.info(
        "AGENT START | reasoning_agent"
    )

    start_time = time.perf_counter()

    gemini_service = (
        GeminiInsightService()
    )

    recommendation_service = (
        RecommendationService()
    )

    updated_insights = []

    # ==========================================
    # Cross-source evidence
    # ==========================================

    combined_evidence = state.get(
        "combined_evidence",
        {}
    )

    logger.info(
        "REASONING EVIDENCE | jira=%s | slack=%s",
        len(
            combined_evidence.get(
                "jira",
                []
            )
        ),
        len(
            combined_evidence.get(
                "slack",
                []
            )
        )
    )

    try:

        for insight in state["insights"]:

            try:

                updated_insight = (
                    gemini_service
                    .generate_insight_analysis(
                        insight,
                        combined_evidence
                    )
                )

            except Exception as e:

                logger.error(
                    "GEMINI ERROR | "
                    "reasoning_agent | %s",
                    e
                )

                recommendation = (
                    recommendation_service
                    .generate_recommendation(
                        insight
                    )
                )

                insight.impact = (
                    recommendation["impact"]
                )

                insight.recommendation = (
                    recommendation[
                        "recommendation"
                    ]
                )

                updated_insight = insight

            updated_insights.append(
                updated_insight
            )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AGENT END | reasoning_agent | "
            "execution_time=%.2fs | "
            "insights=%s",
            execution_time,
            len(updated_insights)
        )

        return {
            "insights": updated_insights
        }

    except Exception:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | reasoning_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        raise