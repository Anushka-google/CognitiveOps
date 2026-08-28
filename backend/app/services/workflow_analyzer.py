from collections import defaultdict

from app.models.insight import Insight
from app.services.recommendation_service import (
    RecommendationService
)
from app.services.gemini_insight_service import (
    GeminiInsightService
)


class WorkflowAnalyzer:

    DELAY_THRESHOLD = 3

    # ----------------------------------------
    # Detect Approval Delays
    # ----------------------------------------

    def detect_delays(self, workflows):

        delayed_workflows = []

        for workflow in workflows:

            print(
                workflow.ticket_id,
                workflow.days_waiting,
                workflow.status
            )

            if workflow.days_waiting > self.DELAY_THRESHOLD:

                delayed_workflows.append(
                    workflow
                )

        if len(delayed_workflows) == 0:
            return []

        evidence = []

        for workflow in delayed_workflows:

            evidence.append(
                f"Ticket: {workflow.ticket_id}\n"
                f"Title: {workflow.title}\n"
                f"Status: {workflow.status}\n"
                f"Priority: {workflow.priority}\n"
                f"Assignee: {workflow.assignee}\n"
                f"Due Date: {workflow.due_date}\n"
                f"Waiting: {workflow.days_waiting} days"
            )

        return [
            Insight(
                issue="Approval Delay",
                evidence=evidence,
                severity="High"
            )
        ]

    # ----------------------------------------
    # Detect Blockers
    # ----------------------------------------

    def detect_blockers(self, workflows):

        blocked = []

        for workflow in workflows:

            if workflow.status == "Blocked":

                blocked.append(
                    workflow
                )

        if len(blocked) == 0:
            return []

        evidence = []

        for workflow in blocked:

            evidence.append(
                f"{workflow.ticket_id} is Blocked"
            )

        return [
            Insight(
                issue="Workflow Blocker",
                evidence=evidence,
                severity="High"
            )
        ]

    # ----------------------------------------
    # Detect Reassignments
    # ----------------------------------------

    def detect_reassignments(self, workflows):

        insights = []

        ticket_assignees = defaultdict(list)

        for workflow in workflows:

            ticket_assignees[
                workflow.ticket_id
            ].append(
                workflow.assignee
            )

        evidence = []

        for ticket_id, assignees in ticket_assignees.items():

            reassignment_count = (
                len(set(assignees)) - 1
            )

            if reassignment_count > 2:

                evidence.append(
                    f"{ticket_id} reassigned "
                    f"{reassignment_count} times"
                )

        if len(evidence) > 0:

            insights.append(
                Insight(
                    issue="Ownership Instability",
                    evidence=evidence,
                    severity="High"
                )
            )

        return insights

    # ----------------------------------------
    # Analyze Workflow
    # ----------------------------------------

    def analyze_workflow(self, workflows):

        insights = []

        insights.extend(
            self.detect_delays(
                workflows
            )
        )

        insights.extend(
            self.detect_blockers(
                workflows
            )
        )

        insights.extend(
            self.detect_reassignments(
                workflows
            )
        )

        recommendation_service = (
            RecommendationService()
        )

        gemini_service = (
            GeminiInsightService()
        )

        updated_insights = []

        for insight in insights:

            try:

                updated = (
                    gemini_service.generate_insight_analysis(
                        insight
                    )
                )

                updated_insights.append(
                    updated
                )

            except Exception as e:

                print(
                    f"Gemini Error : {e}"
                )

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

                updated_insights.append(
                    insight
                )

        return updated_insights