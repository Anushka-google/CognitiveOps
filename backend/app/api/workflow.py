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

router = APIRouter()


@router.post("/workflow/analyze")
def analyze_workflow():

    workflows = [
        WorkflowRecord(
            ticket_id="T1",
            assignee="John",
            status="Blocked",
            days_waiting=5
        ),
        WorkflowRecord(
            ticket_id="T1",
            assignee="Mike",
            status="Blocked",
            days_waiting=5
        )
    ]

    service = (
        WorkflowGraphService()
    )

    result = service.analyze(
        workflows
    )

    return result