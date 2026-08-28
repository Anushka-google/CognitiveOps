import logging
import time

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


def workflow_agent(
    state: AgentState
):

    logger.info(
        "AGENT START | workflow_agent"
    )

    start_time = time.perf_counter()

    try:

        insights = state["insights"]

        total_issues = len(
            insights
        )

        high_severity_issues = sum(
            1
            for insight in insights
            if insight.severity == "High"
        )

        workflow_health = "Healthy"

        if high_severity_issues > 0:

            workflow_health = "Poor"

        summary = (
            f"{total_issues} workflow "
            f"issues detected"
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AGENT END | workflow_agent | "
            "execution_time=%.2fs | "
            "issues=%s | health=%s",
            execution_time,
            total_issues,
            workflow_health
        )

        return {
            "workflow_summary": summary,
            "workflow_health": workflow_health,
            "total_issues": total_issues,
            "high_severity_issues":
                high_severity_issues
        }

    except Exception:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | workflow_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        raise