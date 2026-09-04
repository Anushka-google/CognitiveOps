from typing import Literal
import os

from fastapi import (
    APIRouter,
    HTTPException
)

from pydantic import BaseModel

from app.services.jira_service import JiraService

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

class ApprovalRequest(BaseModel):

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

    # =====================================================
    # 1. VALIDATE ISSUE KEY
    # =====================================================

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
    # 2. REJECTION
    #
    # IMPORTANT:
    # No Jira API mutation occurs.
    # =====================================================

    if request.decision == "reject":

        return {

            "success":
                True,

            "issue_key":
                issue_key,

            "decision":
                "rejected",

            "execution_status":
                "rejected",

            "approval_required":
                True,

            "approval_status":
                "rejected",

            "message":
                (
                    "Human rejected the "
                    "proposed Jira action."
                )
        }

    # =====================================================
    # 3. APPROVAL
    #
    # Re-fetch Jira state.
    # Recalculate risk.
    # Only then mutate Jira.
    # =====================================================

    try:

        jira_service = JiraService()

        # =================================================
        # FETCH CURRENT JIRA DATA
        # =================================================

        workflows = (
            jira_service
            .get_workflow_records()
        )

        # =================================================
        # RECALCULATE CURRENT RISK
        # =================================================

        risk_service = (
            RiskScoringService()
        )

        risk_data = (
            risk_service.calculate(
                workflows
            )
        )

        # =================================================
        # FIND APPROVED TICKET
        # =================================================

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

        # =================================================
        # TICKET NOT FOUND
        # =================================================

        if not matching_ticket:

            raise HTTPException(

                status_code=404,

                detail=(
                    f"Jira ticket "
                    f"{issue_key} was not found."
                )
            )

        # =================================================
        # CURRENT RISK
        # =================================================

        current_risk_level = (
            matching_ticket.get(
                "risk_level"
            )
        )

        current_risk_score = (
            matching_ticket.get(
                "risk_score"
            )
        )

        # =================================================
        # SAFETY GATE
        #
        # The ticket MUST still be High risk.
        # =================================================

        if current_risk_level != "High":

            raise HTTPException(

                status_code=409,

                detail=(
                    f"{issue_key} is no longer "
                    f"High risk. Current risk score: "
                    f"{current_risk_score}"
                )
            )

        # =================================================
        # ACTUAL JIRA MUTATION
        #
        # THIS IS THE ONLY PLACE WHERE THE ACTION EXECUTES.
        # =================================================

        new_priority = "Highest"

        jira_result = (

            jira_service
            .update_issue_priority(

                issue_key,

                new_priority
            )
        )

        # =================================================
        # SUCCESS RESPONSE
        # =================================================

        return {

            "success":
                True,

            "issue_key":
                issue_key,

            "decision":
                "approved",

            "approval_required":
                True,

            "approval_status":
                "approved",

            "execution_status":
                "completed",

            "risk_score":
                current_risk_score,

            "risk_level":
                current_risk_level,

            "action":
                "jira_update_priority",

            "field":
                "priority",

            "new_priority":
                new_priority,

            "jira_result":
                jira_result,

            "message":
                (
                    "Human approval accepted "
                    "and Jira action executed."
                )
        }

    # =====================================================
    # PRESERVE HTTP ERRORS
    # =====================================================

    except HTTPException:

        raise

    # =====================================================
    # UNEXPECTED ERROR
    # =====================================================

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )