from fastapi import APIRouter
import os

from app.services.jira_service import JiraService
from app.services.workflow_graph_service import WorkflowGraphService


router = APIRouter()


# =========================================================
# JIRA DEBUG
# =========================================================

@router.get("/jira/debug")
def jira_debug():

    return {
        "base_url": os.getenv("JIRA_BASE_URL"),
        "email": os.getenv("JIRA_EMAIL"),
        "project": os.getenv("JIRA_PROJECT_KEY"),
        "token_exists": bool(
            os.getenv("JIRA_API_TOKEN")
        )
    }


# =========================================================
# JIRA TEST
# =========================================================

@router.get("/jira/test")
def test_jira():

    try:

        jira_service = JiraService()

        tickets = jira_service.get_workflow_records()

        return tickets

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================================
# JIRA PROJECT CHECK
# =========================================================

@router.get("/jira/project-check")
def jira_project_check():

    try:

        jira_service = JiraService()

        return jira_service.check_project()

    except Exception as e:

        return {
            "error": str(e)
        }

@router.get("/jira/identity-check")
def jira_identity_check():

    try:

        jira_service = JiraService()

        return jira_service.check_identity()

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================================
# ENVIRONMENT CHECK
# =========================================================

@router.get("/jira/env-check")
def env_check():

    return {
        "base_url": os.getenv("JIRA_BASE_URL"),
        "email_exists": bool(
            os.getenv("JIRA_EMAIL")
        ),
        "token_exists": bool(
            os.getenv("JIRA_API_TOKEN")
        ),
        "project_key": os.getenv(
            "JIRA_PROJECT_KEY"
        )
    }


# =========================================================
# WORKFLOW ANALYSIS
# =========================================================

@router.post("/workflow/analyze")
def analyze_workflow():

    try:

        jira_service = JiraService()

        workflows = (
            jira_service.get_workflow_records()
        )

        service = WorkflowGraphService()

        result = service.analyze(
            workflows
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }