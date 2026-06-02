from app.agents.state import AgentState
from app.services.workflow_analyzer import WorkflowAnalyzer


def pattern_agent(state: AgentState):

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

    return {
    "insights": insights
    }