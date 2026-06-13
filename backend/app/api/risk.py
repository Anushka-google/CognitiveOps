from fastapi import APIRouter

from app.services.jira_service import (
    JiraService
)

from app.services.risk_scoring_service import (
    RiskScoringService
)

router = APIRouter()


@router.get("/risk")

def get_risk_scores():

    jira_service = (
        JiraService()
    )

    workflows = (
        jira_service.get_workflow_records()
    )

    risk_service = (
        RiskScoringService()
    )

    result = (
        risk_service.calculate(
            workflows
        )
    )

    return result