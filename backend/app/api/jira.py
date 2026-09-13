import os
from fastapi import APIRouter
from app.services.jira_service import JiraService

router = APIRouter()

# =========================================================
# JIRA DEBUG
# =========================================================

@router.get("/debug")
def jira_debug():
    return {
        "base_url": os.getenv("JIRA_BASE_URL"),
        "email": os.getenv("JIRA_EMAIL"),
        "project": os.getenv("JIRA_PROJECT_KEY"),
        "token_exists": bool(os.getenv("JIRA_API_TOKEN"))
    }

# =========================================================
# JIRA TEST
# =========================================================

@router.get("/test")
def test_jira():
    try:
        jira_service = JiraService()
        tickets = jira_service.get_workflow_records()
        return tickets
    except Exception as e:
        return {"error": str(e)}

# =========================================================
# JIRA PROJECT CHECK
# =========================================================

@router.get("/project-check")
def jira_project_check():
    try:
        jira_service = JiraService()
        return jira_service.check_project()
    except Exception as e:
        return {"error": str(e)}

# =========================================================
# JIRA IDENTITY CHECK
# =========================================================

@router.get("/identity-check")
def jira_identity_check():
    try:
        jira_service = JiraService()
        return jira_service.check_identity()
    except Exception as e:
        return {"error": str(e)}

# =========================================================
# ENVIRONMENT CHECK
# =========================================================

@router.get("/env-check")
def env_check():
    return {
        "base_url": os.getenv("JIRA_BASE_URL"),
        "email_exists": bool(os.getenv("JIRA_EMAIL")),
        "token_exists": bool(os.getenv("JIRA_API_TOKEN"))
    }
