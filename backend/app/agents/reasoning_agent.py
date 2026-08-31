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

    # ==========================================
    # Long-Term Memory
    # ==========================================

    long_term_memory = state.get(
        "long_term_memory",
        []
    )

    logger.info(
        "LONG-TERM MEMORY | "
        "reasoning_agent | count=%s",
        len(long_term_memory)
    )

    try:

        for insight in state["insights"]:

            try:

                analysis_context = {

                    **combined_evidence,

                    "long_term_memory": (
                        long_term_memory
                    )
                }

                logger.info(
                    "REASONING CONTEXT | "
                    "long_term_memory=%s",
                    len(
                        analysis_context.get(
                            "long_term_memory",
                            []
                        )
                    )
                )

                updated_insight = (
                    gemini_service
                    .generate_insight_analysis(
                        insight,
                        analysis_context
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

        # ==========================================
        # Structured Agent Output
        # ==========================================

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        agent_outputs[
            "reasoning_agent"
        ] = {

            "agent": "reasoning_agent",

            "status": "success",

            "output": {

                "insights_count": (
                    len(updated_insights)
                ),

                "gemini_used": True
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        logger.info(
            "STRUCTURED OUTPUT | "
            "agent=reasoning_agent | "
            "status=success"
        )

        return {

            "insights": updated_insights,

            "agent_outputs": agent_outputs
        }

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | reasoning_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        agent_outputs[
            "reasoning_agent"
        ] = {

            "agent": "reasoning_agent",

            "status": "failed",

            "output": None,

            "execution_time": (
                execution_time
            ),

            "error": str(e)
        }

        return {

            "agent_outputs": agent_outputs,

            "errors": [
                str(e)
            ]
        }