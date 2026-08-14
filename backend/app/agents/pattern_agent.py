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

    insights = list(unique.values())

    print(f"TOTAL INSIGHTS : {len(insights)}")

    return {
        "insights": insights
    }