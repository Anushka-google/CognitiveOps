import logging
import time

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


def recommendation_agent(
    state: AgentState
):
    """
    Processes generated recommendations
    and returns a structured agent output.

    Agent responsibilities:
    - Process insights
    - Mark high-priority recommendations
    - Return predictable output structure

    It does not:
    - call external APIs
    - call Gemini
    - retrieve evidence
    - modify workflow data
    """

    logger.info(
        "AGENT START | recommendation_agent"
    )

    start_time = time.perf_counter()

    try:

        # ==========================================
        # Read existing insights
        # ==========================================

        insights = state.get(
            "insights",
            []
        )

        high_priority_count = 0

        # ==========================================
        # Process recommendations
        # ==========================================

        for insight in insights:

            if (
                insight.severity == "High"
                and insight.recommendation
            ):

                # Avoid adding the prefix repeatedly
                if not insight.recommendation.startswith(
                    "[HIGH PRIORITY]"
                ):

                    insight.recommendation = (
                        "[HIGH PRIORITY] "
                        + insight.recommendation
                    )

                high_priority_count += 1

        # ==========================================
        # Execution time
        # ==========================================

        execution_time = (
            time.perf_counter()
            - start_time
        )

        # ==========================================
        # Structured Agent Output
        # ==========================================

        recommendation_output = {

            "status": "success",

            "result_count": (
                len(insights)
            ),

            "high_priority_count": (
                high_priority_count
            ),

            "output": insights
        }

        # ==========================================
        # Logging
        # ==========================================

        logger.info(
            "AGENT END | recommendation_agent | "
            "execution_time=%.2fs | "
            "high_priority=%s",
            execution_time,
            high_priority_count
        )

        logger.info(
            "STRUCTURED OUTPUT | "
            "agent=recommendation_agent | "
            "status=%s | "
            "result_count=%s",
            recommendation_output["status"],
            recommendation_output["result_count"]
        )

        # ==========================================
        # Return State Update
        # ==========================================

        return {

            "insights": insights,

            "agent_outputs": {

                **state.get(
                    "agent_outputs",
                    {}
                ),

                "recommendation_agent": (
                    recommendation_output
                )
            }
        }

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | recommendation_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        # ==========================================
        # Structured Error Output
        # ==========================================

        error_output = {

            "status": "error",

            "result_count": 0,

            "high_priority_count": 0,

            "output": [],

            "error": str(e)
        }

        return {

            "agent_outputs": {

                **state.get(
                    "agent_outputs",
                    {}
                ),

                "recommendation_agent": (
                    error_output
                )
            },

            "errors": [

                *state.get(
                    "errors",
                    []
                ),

                {
                    "agent": (
                        "recommendation_agent"
                    ),
                    "error": str(e)
                }
            ]
        }