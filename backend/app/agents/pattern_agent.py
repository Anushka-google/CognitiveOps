from app.agents.state import AgentState
from app.services.workflow_analyzer import WorkflowAnalyzer


def pattern_agent(state: AgentState):
    print("==================================")
    print("Running Pattern Agent")
    print("==================================")

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