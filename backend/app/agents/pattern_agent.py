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

        # ==========================================
        # Remove duplicate insights
        # ==========================================

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
            "pattern_agent"
        ] = {

            "agent": "pattern_agent",

            "status": "success",

            "output": {

                "insights_count": len(
                    insights
                )
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        logger.info(
            "STRUCTURED OUTPUT | "
            "agent=pattern_agent | "
            "status=success"
        )

        return {

            "insights": insights,

            "agent_outputs": agent_outputs
        }

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | pattern_agent | "
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
            "pattern_agent"
        ] = {

            "agent": "pattern_agent",

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