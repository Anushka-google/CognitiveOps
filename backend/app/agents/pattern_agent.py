import logging
import time

from app.agents.state import AgentState
from app.services.workflow_analyzer import (
    WorkflowAnalyzer
)


logger = logging.getLogger(__name__)


def pattern_agent(
    state: AgentState
):

    logger.info(
        "AGENT START | pattern_agent"
    )

    start_time = time.perf_counter()

    try:

        analyzer = WorkflowAnalyzer()

        insights = []

        insights.extend(
            analyzer.detect_delays(
                state["workflows"]
            )
        )

        insights.extend(
            analyzer.detect_blockers(
                state["workflows"]
            )
        )

        insights.extend(
            analyzer.detect_reassignments(
                state["workflows"]
            )
        )

        # -----------------------------
        # Remove duplicate insights
        # -----------------------------

        unique = {}

        for insight in insights:

            key = (
                insight.issue,
                insight.severity
            )

            if key not in unique:

                unique[key] = insight

        insights = list(
            unique.values()
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AGENT END | pattern_agent | "
            "execution_time=%.2fs | insights=%s",
            execution_time,
            len(insights)
        )

        return {
            "insights": insights
        }

    except Exception:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | pattern_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        raise