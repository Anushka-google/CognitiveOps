from app.agents.state import AgentState


def workflow_agent(
    state: AgentState
):
    print("==================================")
    print("Running Workflow Agent")
    print("==================================")

    insights = state["insights"]

    total_issues = len(insights)

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

    return {
        "workflow_summary": summary,
        "workflow_health": workflow_health,
        "total_issues": total_issues,
        "high_severity_issues":
            high_severity_issues
    }