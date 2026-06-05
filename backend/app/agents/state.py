from typing import TypedDict

from app.models.workflow import WorkflowRecord
from app.models.insight import Insight


class AgentState(TypedDict):
    workflows: list[WorkflowRecord]
    insights: list[Insight]

    workflow_summary: str | None

    workflow_health: str | None
    total_issues: int
    high_severity_issues: int