from collections import defaultdict

from app.models.insight import Insight
from app.services.recommendation_service import RecommendationService
from app.services.gemini_insight_service import (
    GeminiInsightService
)


class WorkflowAnalyzer:

    DELAY_THRESHOLD = 3

    def detect_delays(self, workflows):

        insights = []
        processed_tickets = set()

        for workflow in workflows:

            print(
                workflow.ticket_id,
                workflow.days_waiting,
                workflow.status
            )

            if workflow.ticket_id in processed_tickets:
                continue

            if workflow.days_waiting > self.DELAY_THRESHOLD:

                print(
                    f"DELAY DETECTED: "
                    f"{workflow.ticket_id}"
                )

                insights.append(
                    Insight(
                        issue="Approval Delay",
                        evidence=[
                            f"Ticket {workflow.ticket_id} "
                            f"waiting for "
                            f"{workflow.days_waiting} days"
                        ],
                        severity="High"
                    )
                )

                processed_tickets.add(
                    workflow.ticket_id
                )

        return insights

    def detect_blockers(self, workflows):

        insights = []
        processed_tickets = set()

        for workflow in workflows:

            if workflow.ticket_id in processed_tickets:
                continue

            if workflow.status == "Blocked":

                insights.append(
                    Insight(
                        issue="Workflow Blocker",
                        evidence=[
                            f"Ticket {workflow.ticket_id} is blocked"
                        ],
                        severity="High"
                    )
                )

                processed_tickets.add(
                    workflow.ticket_id
                )

        return insights

    def detect_reassignments(self, workflows):

        insights = []
        ticket_assignees = defaultdict(list)

        for workflow in workflows:
            ticket_assignees[
                workflow.ticket_id
            ].append(
                workflow.assignee
            )

        for ticket_id, assignees in ticket_assignees.items():

            reassignment_count = (
                len(set(assignees)) - 1
            )

            if reassignment_count > 2:

                insights.append(
                    Insight(
                        issue="Ownership Instability",
                        evidence=[
                            f"Ticket {ticket_id} "
                            f"reassigned "
                            f"{reassignment_count} times"
                        ],
                        severity="High"
                    )
                )

        return insights

    def analyze_workflow(self, workflows):

        insights = []

        insights.extend(
            self.detect_delays(workflows)
        )

        insights.extend(
            self.detect_blockers(workflows)
        )

        insights.extend(
            self.detect_reassignments(workflows)
        )

        recommendation_service = (
            RecommendationService()
        )

        gemini_service = (
            GeminiInsightService()
        )

        for insight in insights:

            try:
                insights=(
                gemini_service.generate_insight_analysis(
                    insight
                )
                )

            except Exception:

                print(
                    f"Gemini Error: {e}"
                )

                recommendation = (
                    recommendation_service
                    .generate_recommendation(
                        insight
                    )
                )

                insight.impact = (
                    recommendation["impact"]
                )

                insight.recommendation = (
                    recommendation[
                        "recommendation"
                    ]
                )

        return insights