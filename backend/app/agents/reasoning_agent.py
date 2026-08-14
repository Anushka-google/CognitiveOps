from app.agents.state import AgentState
from app.services.gemini_insight_service import (
    GeminiInsightService
)
from app.services.recommendation_service import (
    RecommendationService
)


def reasoning_agent(state: AgentState):

    print("==================================")
    print("Running Reasoning Agent")
    print("==================================")

    gemini_service = GeminiInsightService()
    recommendation_service = RecommendationService()

    updated_insights = []

    for insight in state["insights"]:

        try:

            updated_insight = (
                gemini_service.generate_insight_analysis(
                    insight
                )
            )

        except Exception as e:

            print(f"Gemini Error : {e}")

            recommendation = (
                recommendation_service.generate_recommendation(
                    insight
                )
            )

            insight.impact = (
                recommendation["impact"]
            )

            insight.recommendation = (
                recommendation["recommendation"]
            )

            updated_insight = insight

        updated_insights.append(
            updated_insight
        )

    return {
        "insights": updated_insights
    }