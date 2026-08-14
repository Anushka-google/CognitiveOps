from app.models.insight import Insight


class RecommendationService:

    def generate_recommendation(
        self,
        insight: Insight
    ):

        if insight.issue == "Approval Delay":

            return {

                "impact":
                (
                    "Multiple Jira tickets have exceeded the approval "
                    "threshold, increasing workflow cycle time and "
                    "raising the risk of SLA violations."
                ),

                "recommendation":
                (
                    "Review the approval queue, escalate overdue "
                    "tickets, and redistribute approvals among "
                    "available team members."
                )
            }

        if insight.issue == "Workflow Blocker":

            return {

                "impact":
                (
                    "Blocked tickets are preventing downstream "
                    "workflow execution and delaying project delivery."
                ),

                "recommendation":
                (
                    "Identify the blocker owner, resolve the "
                    "dependency, and monitor blocked items daily."
                )
            }

        if insight.issue == "Ownership Instability":

            return {

                "impact":
                (
                    "Frequent ownership changes reduce accountability "
                    "and increase delivery delays."
                ),

                "recommendation":
                (
                    "Assign a primary owner for the complete ticket "
                    "lifecycle and limit unnecessary reassignments."
                )
            }

        return {

            "impact":
            (
                "Potential workflow inefficiency detected."
            ),

            "recommendation":
            (
                "Review the workflow and investigate the issue."
            )
        }