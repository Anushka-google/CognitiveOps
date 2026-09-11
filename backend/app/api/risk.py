from fastapi import APIRouter

from app.services.jira_service import (
    JiraService
)

from app.services.risk_scoring_service import (
    RiskScoringService
)

from app.services.sla_predictor import (
    SLAPredictor
)


router = APIRouter()


@router.get(
    "/risk"
)
def get_risk_scores():

    jira_service = (
        JiraService()
    )

    workflows = (
        jira_service
        .get_workflow_records()
    )

    risk_service = (
        RiskScoringService()
    )

    result = (
        risk_service.calculate(
            workflows
        )
    )

    # =========================
    # SLA PREDICTION
    # =========================

    sla_predictor = (
        SLAPredictor()
    )

    if workflows:

        workflow = workflows[0].model_dump()

        days_waiting = float(
            workflow.get(
                "days_waiting",
                0
            )
        )

        backlog_age_hours = (
            days_waiting * 24
        )

        response_time_hours = float(
            workflow.get(
                "response_time_hours",
                0
            )
        )

        waiting_ratio = (
            backlog_age_hours
            / (
                backlog_age_hours
                + response_time_hours
                + 1e-6
            )
        )

        sla_features = {

            "customer_tenure_months":
                float(
                    workflow.get(
                        "customer_tenure_months",
                        0
                    )
                ),

            "previous_tickets_90d":
                float(
                    workflow.get(
                        "previous_tickets_90d",
                        0
                    )
                ),

            "avg_sentiment_score":
                float(
                    workflow.get(
                        "avg_sentiment_score",
                        0
                    )
                ),

            "message_length":
                float(
                    workflow.get(
                        "message_length",
                        0
                    )
                ),

            "contains_urgent_keyword":
                float(
                    workflow.get(
                        "contains_urgent_keyword",
                        0
                    )
                ),

            "contains_refund_keyword":
                float(
                    workflow.get(
                        "contains_refund_keyword",
                        0
                    )
                ),

            "agent_queue_length_at_submit":
                float(
                    workflow.get(
                        "agent_queue_length_at_submit",
                        0
                    )
                ),

            "agent_experience_months":
                float(
                    workflow.get(
                        "agent_experience_months",
                        0
                    )
                ),

            "backlog_age_hours":
                backlog_age_hours,

            "response_time_hours":
                response_time_hours,

            "waiting_ratio":
                waiting_ratio,

            "blocker_density":
                float(
                    workflow.get(
                        "blocker_density",
                        0
                    )
                ),

            "reassignment_rate":
                float(
                    workflow.get(
                        "reassignment_rate",
                        0
                    )
                ),

            "dependency_count":
                float(
                    workflow.get(
                        "dependency_count",
                        0
                    )
                ),

            "workflow_complexity":
                float(
                    workflow.get(
                        "workflow_complexity",
                        0
                    )
                )
        }

        sla_prediction = (
            sla_predictor.predict(
                sla_features
            )
        )

    else:

        sla_prediction = {
            "sla_breach_probability": 0.0,
            "risk_level": "Low"
        }

    result[
        "sla_prediction"
    ] = sla_prediction

    return result