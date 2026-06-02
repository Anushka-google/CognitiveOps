from fastapi import APIRouter

from app.models.workflow import WorkflowRecord
from app.services.workflow_analyzer import WorkflowAnalyzer

router = APIRouter()


@router.post("/analyze")
def analyze_workflow(
    workflows: list[WorkflowRecord]
):

    analyzer = WorkflowAnalyzer()

    insights = analyzer.analyze_workflow(
        workflows
    )

    return {
        "insights": insights
    }