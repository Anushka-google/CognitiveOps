from app.agents.state import AgentState
from app.services.gemini_insight_service import (
    GeminiInsightService
)


def reasoning_agent(state: AgentState):

    print("==================================")
    print("Running Reasoning Agent")
    print("==================================")

    gemini_service = GeminiInsightService()

    updated_insights = []

    for insight in state["insights"]:

        try:

            updated_insight = (
                gemini_service.generate_insight_analysis(
                    insight
                )
            )

        except Exception as e:

            print(
                f"Gemini Error: {e}"
            )

            insight.impact = (
                "Impact unavailable due to API issue."
            )

            insight.recommendation = (
                "Retry analysis later."
            )

            updated_insight = insight

        updated_insights.append(
            updated_insight
        )

    return {
        "insights": updated_insights
    }