from app.agents.state import AgentState
from app.services.gemini_insight_service import (
    GeminiInsightService
)


def reasoning_agent(state: AgentState):

    gemini_service = GeminiInsightService()

    updated_insights = []

    for insight in state["insights"]:

        updated_insight = (
            gemini_service.generate_insight_analysis(
                insight
            )
        )

        updated_insights.append(
            updated_insight
        )

    return {
        "insights": updated_insights
    }