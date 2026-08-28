import logging
import time

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


def recommendation_agent(
    state: AgentState
):

    logger.info(
        "AGENT START | recommendation_agent"
    )

    start_time = time.perf_counter()

    try:

        high_priority_count = 0

        for insight in state["insights"]:

            if (
                insight.severity == "High"
                and insight.recommendation
            ):

                insight.recommendation = (
                    "[HIGH PRIORITY] "
                    + insight.recommendation
                )

                high_priority_count += 1

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AGENT END | recommendation_agent | "
            "execution_time=%.2fs | "
            "high_priority=%s",
            execution_time,
            high_priority_count
        )

        return {
            "insights": state["insights"]
        }

    except Exception:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | recommendation_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        raise