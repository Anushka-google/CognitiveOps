from app.agents.state import AgentState


def route_after_pattern(
    state: AgentState
):

    if state["insights"]:
        return "workflow_agent"

    return "end"