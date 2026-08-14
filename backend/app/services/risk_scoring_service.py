class RiskScoringService:

    def calculate(
        self,
        workflows
    ):

        results = []

        for workflow in workflows:

            score = 0

            # ------------------------
            # Days Waiting
            # ------------------------
            score += min(
                workflow.days_waiting * 5,
                40
            )

            # ------------------------
            # Priority
            # ------------------------
            priority = (
                workflow.priority.lower()
                if workflow.priority
                else ""
            )

            if priority in [
                "highest",
                "critical"
            ]:
                score += 35

            elif priority == "high":
                score += 25

            elif priority == "medium":
                score += 15

            else:
                score += 5

            # ------------------------
            # Status
            # ------------------------
            status = (
                workflow.status.lower()
                if workflow.status
                else ""
            )

            if status == "blocked":
                score += 25

            elif status in [
                "in progress",
                "in review"
            ]:
                score += 10

            # ------------------------
            # Unassigned
            # ------------------------
            assignee = (
                workflow.assignee.lower()
                if workflow.assignee
                else ""
            )

            if assignee == "unassigned":
                score += 10

            score = min(score, 100)

            # ------------------------
            # Risk Level
            # ------------------------
            if score >= 70:
                level = "High"

            elif score >= 40:
                level = "Medium"

            else:
                level = "Low"

            # ------------------------
            # Recommendation
            # ------------------------
            if level == "High":
                recommendation = (
                    "Immediate attention required"
                )

            elif level == "Medium":
                recommendation = (
                    "Monitor closely"
                )

            else:
                recommendation = (
                    "No action needed"
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

        if not results:

            return {

                "average_risk": 0,

                "high_risk_tickets": 0,

                "tickets": []

            }

        high_risk = len(

            [
                r
                for r in results
                if r["risk_level"] == "High"
            ]

        )

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