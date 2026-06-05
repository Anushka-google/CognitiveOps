from app.agents.state import AgentState


def recommendation_agent(
    state: AgentState
):

    print("Running Recommendation Agent")

    for insight in state["insights"]:

        if (
            insight.severity == "High"
            and insight.recommendation
        ):

            insight.recommendation = (
                "[HIGH PRIORITY] "
                + insight.recommendation
            )

    return {
        "insights": state["insights"]
    }