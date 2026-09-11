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

from app.services.root_cause_graph_service import (
    RootCauseGraphService
)

from app.services.risk_scoring_service import (
    RiskScoringService
)

from app.services.executive_intelligence_service import (
    ExecutiveIntelligenceService
)

from app.services.sla_predictor import (
    SLAPredictor
)

from app.services.trend_forecasting_service import (
    TrendForecastingService
)

import logging

logger = logging.getLogger(__name__)


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
# ROOT CAUSE GRAPH
#
# Phase 5.1
#
# This endpoint builds a separate operational graph
# from Jira issue relationships.
#
# It does NOT use the existing LangGraph agent graph.
# =========================================================

@router.get(
    "/workflow/root-cause-graph"
)
def get_root_cause_graph():

    try:

        # -----------------------------------------------------
        # FETCH RAW JIRA ISSUES
        # -----------------------------------------------------

        jira_service = JiraService()

        issues = (
            jira_service
            .get_tickets()
        )

        # -----------------------------------------------------
        # BUILD ROOT CAUSE GRAPH
        # -----------------------------------------------------

        graph_service = (
            RootCauseGraphService()
        )

        result = (
            graph_service
            .build_graph(
                issues
            )
        )

        return result

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Unable to build "
                f"root cause graph: {e}"
            )
        )


# =========================================================
# EXECUTIVE INTELLIGENCE SUMMARY
#
# Phase 5.3 (#72)
# =========================================================

@router.get(
    "/workflow/executive-summary"
)
def get_executive_summary():

    try:

        jira_service = JiraService()

        workflows = (
            jira_service
            .get_workflow_records()
        )

        raw_issues = (
            jira_service
            .get_tickets()
        )

        graph_service = (
            RootCauseGraphService()
        )

        root_cause_graph = (
            graph_service
            .build_graph(
                raw_issues
            )
        )

        # SLA Prediction
        sla_prediction = {
            "sla_breach_probability": 0.0,
            "risk_level": "Low"
        }

        if workflows:

            workflow = workflows[0]
            w_dict = (
                workflow.model_dump()
                if hasattr(workflow, "model_dump")
                else (
                    workflow.dict()
                    if hasattr(workflow, "dict")
                    else dict(workflow)
                )
            )

            days_waiting = float(
                w_dict.get("days_waiting", 0)
            )

            backlog_age_hours = (
                days_waiting * 24
            )

            response_time_hours = float(
                w_dict.get("response_time_hours", 0)
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
                "customer_tenure_months": float(w_dict.get("customer_tenure_months", 0)),
                "previous_tickets_90d": float(w_dict.get("previous_tickets_90d", 0)),
                "avg_sentiment_score": float(w_dict.get("avg_sentiment_score", 0)),
                "message_length": float(w_dict.get("message_length", 0)),
                "contains_urgent_keyword": float(w_dict.get("contains_urgent_keyword", 0)),
                "contains_refund_keyword": float(w_dict.get("contains_refund_keyword", 0)),
                "agent_queue_length_at_submit": float(w_dict.get("agent_queue_length_at_submit", 0)),
                "agent_experience_months": float(w_dict.get("agent_experience_months", 0)),
                "backlog_age_hours": backlog_age_hours,
                "response_time_hours": response_time_hours,
                "waiting_ratio": waiting_ratio,
                "blocker_density": float(w_dict.get("blocker_density", 0)),
                "reassignment_rate": float(w_dict.get("reassignment_rate", 0)),
                "dependency_count": float(w_dict.get("dependency_count", 0)),
                "workflow_complexity": float(w_dict.get("workflow_complexity", 0)),
            }

            try:
                sla_predictor = SLAPredictor()
                sla_prediction = sla_predictor.predict(sla_features)
            except Exception as ex:
                logger.warning("Could not compute SLA prediction: %s", ex)

        # Risk scoring
        risk_service = RiskScoringService()
        risk_result = risk_service.calculate(workflows)

        exec_service = ExecutiveIntelligenceService()

        summary = exec_service.generate_summary(
            workflows=workflows,
            root_cause_graph=root_cause_graph,
            sla_prediction=sla_prediction,
            workflow_health=risk_result.get("overall_risk_level"),
        )

        return summary

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate executive summary: {e}"
        )


# =========================================================
# TREND FORECASTING
#
# Phase 5.4 (#71) — DEFERRED
# =========================================================

@router.get(
    "/workflow/trend-forecast"
)
def get_trend_forecast():

    service = TrendForecastingService()

    return service.get_forecast()


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