from app.models.insight import Insight


class RecommendationService:

    def generate_recommendation(
        self,
        insight: Insight
    ):

        if insight.issue == "Approval Delay":

            return {
                "impact": "Delayed approvals can slow project delivery.",
                "recommendation": "Reduce approval layers or define approval SLAs."
            }

        if insight.issue == "Workflow Blocker":

            return {
                "impact": "Blocked tasks can halt workflow progress.",
                "recommendation": "Identify blocker owner and resolve dependency quickly."
            }

        if insight.issue == "Ownership Instability":

            return {
                "impact": "Frequent reassignments reduce accountability.",
                "recommendation": "Assign a single owner for the ticket lifecycle."
            }

        return {
            "impact": "Unknown impact",
            "recommendation": "Further investigation required."
        }