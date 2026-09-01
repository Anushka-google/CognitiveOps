from typing import Literal
import os

from fastapi import (
    APIRouter,
    HTTPException
)

from pydantic import BaseModel

from app.services.jira_service import (
    JiraService
)

from app.services.workflow_graph_service import (
    WorkflowGraphService
)

from app.services.risk_scoring_service import (
    RiskScoringService
)


router = APIRouter()


# =========================================================
# APPROVAL REQUEST MODEL
# =========================================================

class ApprovalRequest(
    BaseModel
):

    issue_key: str

    decision: Literal[
        "approve",
        "reject"
    ]


# =========================================================
# JIRA DEBUG
# =========================================================

@router.get(
    "/jira/debug"
)
def jira_debug():

    return {

        "base_url":
            os.getenv(
                "JIRA_BASE_URL"
            ),

        "email":
            os.getenv(
                "JIRA_EMAIL"
            ),

        "project":
            os.getenv(
                "JIRA_PROJECT_KEY"
            ),

        "token_exists":
            bool(
                os.getenv(
                    "JIRA_API_TOKEN"
                )
            )

    }


# =========================================================
# JIRA TEST
# =========================================================

@router.get(
    "/jira/test"
)
def test_jira():

    try:

        jira_service = JiraService()

        tickets = (
            jira_service
            .get_workflow_records()
        )

        return tickets

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================================
# JIRA PROJECT CHECK
# =========================================================

@router.get(
    "/jira/project-check"
)
def jira_project_check():

    try:

        jira_service = JiraService()

        return (
            jira_service
            .check_project()
        )

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================================
# JIRA IDENTITY CHECK
# =========================================================

@router.get(
    "/jira/identity-check"
)
def jira_identity_check():

    try:

        jira_service = JiraService()

        return (
            jira_service
            .check_identity()
        )

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================================
# ENVIRONMENT CHECK
# =========================================================

@router.get(
    "/jira/env-check"
)
def env_check():

    return {

        "base_url":
            os.getenv(
                "JIRA_BASE_URL"
            ),

        "email_exists":
            bool(
                os.getenv(
                    "JIRA_EMAIL"
                )
            ),

        "token_exists":
            bool(
                os.getenv(
                    "JIRA_API_TOKEN"
                )
            ),

        "project_key":
            os.getenv(
                "JIRA_PROJECT_KEY"
            )

    }


# =========================================================
# WORKFLOW ANALYSIS
# =========================================================

@router.post(
    "/workflow/analyze"
)
def analyze_workflow():

    try:

        jira_service = JiraService()

        workflows = (
            jira_service
            .get_workflow_records()
        )

        service = (
            WorkflowGraphService()
        )

        result = service.analyze(
            workflows
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================================
# HUMAN APPROVAL
# =========================================================

@router.post(
    "/workflow/approval"
)
def workflow_approval(
    request: ApprovalRequest
):

    issue_key = (
        request.issue_key
        .strip()
    )

    if not issue_key:

        raise HTTPException(
            status_code=400,
            detail=(
                "issue_key is required"
            )
        )

    # =====================================================
    # REJECTION
    # =====================================================

    if request.decision == "reject":

        return {

            "success": True,

            "issue_key":
                issue_key,

            "decision":
                "rejected",

            "execution_status":
                "rejected",

            "message":
                "Human rejected the proposed Jira action."

        }

    # =====================================================
    # APPROVAL
    #
    # IMPORTANT:
    # Re-check Jira risk before performing the mutation.
    #
    # This prevents a stale approval from changing a ticket
    # whose current state is no longer high risk.
    # =====================================================

    try:

        jira_service = JiraService()

        workflows = (
            jira_service
            .get_workflow_records()
        )

        risk_service = (
            RiskScoringService()
        )

        risk_data = (
            risk_service.calculate(
                workflows
            )
        )

        matching_ticket = next(
            (
                ticket

                for ticket
                in risk_data.get(
                    "tickets",
                    []
                )

                if ticket.get(
                    "ticket_id"
                ) == issue_key
            ),
            None
        )

        if not matching_ticket:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Jira ticket "
                    f"{issue_key} was not found."
                )
            )

        # =================================================
        # SAFETY CHECK
        # =================================================

        if matching_ticket.get(
            "risk_level"
        ) != "High":

            raise HTTPException(
                status_code=409,
                detail=(
                    f"{issue_key} is no longer "
                    f"High risk. Current risk score: "
                    f"{matching_ticket.get('risk_score')}"
                )
            )

        # =================================================
        # EXECUTE APPROVED ACTION
        # =================================================

        jira_result = (
            jira_service
            .update_issue_priority(
                issue_key,
                "Highest"
            )
        )

        return {

            "success": True,

            "issue_key":
                issue_key,

            "decision":
                "approved",

            "execution_status":
                "completed",

            "risk_score":
                matching_ticket.get(
                    "risk_score"
                ),

            "risk_level":
                matching_ticket.get(
                    "risk_level"
                ),

            "action":
                "jira_update_priority",

            "new_priority":
                "Highest",

            "jira_result":
                jira_result,

            "message":
                "Human approval accepted and Jira action executed."

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )