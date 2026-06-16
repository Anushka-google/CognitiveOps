from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from app.services.file_service import (
    save_uploaded_file
)

from app.services.workflow_csv_parser import (
    parse_workflow_csv
)


from app.models.workflow import (
    WorkflowRecord
)

from app.services.workflow_graph_service import (
    WorkflowGraphService
)

from app.services.jira_service import (
    JiraService
)

router = APIRouter()



@router.get(
    "/jira/test"
)
def test_jira():

    service = JiraService()

    tickets = (
        service.get_tickets()
    )

    return tickets[:5]

@router.post("/workflow/analyze")
def analyze_workflow():

    jira_service = (
        JiraService()
    )

    workflows = (
    jira_service.get_workflow_records()
)
    service = (
        WorkflowGraphService()
    )

    result = service.analyze(
        workflows
    )

    return result

@router.get("/jira/debug")
def jira_debug():
    import os

    return {
        "base_url": os.getenv("JIRA_BASE_URL"),
        "email": os.getenv("JIRA_EMAIL"),
        "project": os.getenv("JIRA_PROJECT_KEY"),
        "token_exists": bool(
            os.getenv("JIRA_API_TOKEN")
        )
    }

    