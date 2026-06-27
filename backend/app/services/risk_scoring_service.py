class RiskScoringService:

    def calculate(
        self,
        workflows
    ):

        results = []

        for workflow in workflows:

            score = min(
                workflow.days_waiting * 10,
                100
            )

            if score >= 70:
                level = "High"

            elif score >= 40:
                level = "Medium"

            else:
                level = "Low"

            recommendation = (
                "Immediate attention required"
                if level == "High"
                else "Monitor closely"
                if level == "Medium"
                else "No action needed"
            )

            results.append(
                {
                    "ticket_id":
                    workflow.ticket_id,

                    "risk_score":
                    score,

                    "risk_level":
                    level,

                    "recommendation":
                    recommendation
                }
            )

        high_risk = len(
            [
                r for r in results
                if r["risk_level"] == "High"
            ]
        )

        if not results:
            return {
                "average_risk":0,
                "high_risk_tickets":0,
                "tickets":[]
            }

        average_risk = round(
            sum(
                r["risk_score"]
                for r in results
            ) / len(results),
            2
        )

        return {
            "average_risk":
            average_risk,

            "high_risk_tickets":
            high_risk,

            "tickets":
            results
        }