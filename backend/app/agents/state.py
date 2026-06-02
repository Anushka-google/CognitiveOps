from typing import TypedDict

from app.models.workflow import WorkflowRecord
from app.models.insight import Insight


class AgentState(TypedDict):
    workflows: list[WorkflowRecord]
    insights: list[Insight]
    workflow_summary: str | None