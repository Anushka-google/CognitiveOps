from app.agents.state import AgentState


def workflow_agent(
    state: AgentState
):

    print("Running Workflow Agent")

    insight_count = len(
        state["insights"]
    )

    summary = (
        f"{insight_count} workflow "
        f"issues detected"
    )

    return {
        "workflow_summary":
            summary
    }