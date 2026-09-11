from app.services.sla_feature_service import SLAFeatureService
from app.services.sla_predictor import SLAPredictor


class RiskScoringService:

    def _build_sla_decision(
        self,
        sla_prediction,
        sla_features
    ):

        risk_level = sla_prediction.get(
            "risk_level",
            "Unknown"
        )

        factors = []

        if sla_features.get(
            "backlog_age_hours",
            0
        ) >= 48:

            factors.append(
                "High backlog age"
            )

        if sla_features.get(
            "waiting_ratio",
            0
        ) >= 0.70:

            factors.append(
                "High waiting ratio"
            )

        if sla_features.get(
            "blocker_density",
            0
        ) > 0:

            factors.append(
                "Workflow blockers detected"
            )

        if sla_features.get(
            "reassignment_rate",
            0
        ) > 0:

            factors.append(
                "Frequent reassignment activity"
            )

        if sla_features.get(
            "dependency_count",
            0
        ) > 0:

            factors.append(
                "Workflow dependencies detected"
            )

        if sla_features.get(
            "workflow_complexity",
            0
        ) >= 5:

            factors.append(
                "High workflow complexity"
            )

        if sla_features.get(
            "agent_queue_length_at_submit",
            0
        ) >= 5:

            factors.append(
                "High agent queue length"
            )

        if sla_features.get(
            "response_time_hours",
            0
        ) >= 24:

            factors.append(
                "Slow response time"
            )

        if not factors:

            factors.append(
                "No major SLA risk factor detected"
            )

        if risk_level == "High":

            explanation = (
                "The TensorFlow SLA model predicts a high "
                "probability of SLA breach based on the "
                "current workflow features and waiting conditions."
            )

            recommendation = (
                "Prioritize this workflow and address the "
                "identified contributing factors immediately."
            )

        elif risk_level == "Medium":

            explanation = (
                "The TensorFlow SLA model indicates a moderate "
                "probability of SLA breach."
            )

            recommendation = (
                "Monitor the workflow closely and address "
                "the identified contributing factors."
            )

        else:

            explanation = (
                "The TensorFlow SLA model predicts a low "
                "probability of SLA breach."
            )

            recommendation = (
                "Continue normal monitoring."
            )

        return {
            "risk_level":
                risk_level,

            "contributing_factors":
                factors,

            "explanation":
                explanation,

            "recommendation":
                recommendation
        }

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

            score = min(
                score,
                100
            )

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

                "average_risk":
                    0,

                "high_risk_tickets":
                    0,

                "tickets":
                    []

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

        # =====================================================
        # SLA PREDICTION
        # =====================================================

        sla_prediction = {
            "sla_breach_probability": None,
            "risk_level": "Unknown"
        }

        sla_decision = {
            "risk_level": "Unknown",
            "contributing_factors": [],
            "explanation": (
                "SLA prediction is currently unavailable."
            ),
            "recommendation": (
                "No SLA recommendation is currently available."
            )
        }

        try:

            # ---------------------------------------------
            # Select the highest-risk workflow
            # ---------------------------------------------

            highest_risk_index = max(
                range(len(results)),
                key=lambda index:
                    results[index]["risk_score"]
            )

            selected_workflow = (
                workflows[highest_risk_index]
            )

            # ---------------------------------------------
            # Build live SLA features
            # ---------------------------------------------

            feature_service = SLAFeatureService()

            sla_features = (
                feature_service.build_features(
                    selected_workflow,
                    workflows
                )
            )

            # ---------------------------------------------
            # Run TensorFlow prediction
            # ---------------------------------------------

            predictor = SLAPredictor()

            sla_prediction = predictor.predict(
                sla_features
            )

            # ---------------------------------------------
            # Build explainable SLA decision
            # ---------------------------------------------

            sla_decision = self._build_sla_decision(
                sla_prediction,
                sla_features
            )

        except Exception as e:

            sla_prediction = {
                "sla_breach_probability": None,
                "risk_level": "Unknown",
                "error": str(e)
            }

            sla_decision = {
                "risk_level": "Unknown",
                "contributing_factors": [],
                "explanation": (
                    "SLA prediction could not be generated."
                ),
                "recommendation": (
                    "No SLA recommendation is currently available."
                ),
                "error": str(e)
            }

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {

            "average_risk":
                average_risk,

            "high_risk_tickets":
                high_risk,

            "tickets":
                results,

            "sla_prediction":
                sla_prediction,

            "sla_decision":
                sla_decision

        }