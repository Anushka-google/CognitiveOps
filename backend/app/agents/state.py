from typing import TypedDict

from app.models.workflow import WorkflowRecord
from app.models.insight import Insight


class AgentState(TypedDict, total=False):
    # =====================================================
    # Core workflow data
    # =====================================================

    workflows: list[WorkflowRecord]

    insights: list[Insight]

    # =====================================================
    # User / Intent
    # =====================================================

    user_goal: str | None

    intent: str | None

    # =====================================================
    # Planner
    # =====================================================

    plan: list[str]

    current_step: int

    # =====================================================
    # Workflow Analysis
    # =====================================================

    workflow_summary: str | None

    workflow_health: str | None

    total_issues: int

    high_severity_issues: int

    delayed_workflows: list[WorkflowRecord]

    # =====================================================
    # Evidence
    # =====================================================

    jira_evidence: list

    slack_evidence: list

    combined_evidence: dict

    # =====================================================
    # Observation
    # =====================================================

    observation: dict

    observations: list[dict]

    # =====================================================
    # Execution
    # =====================================================

    execution_status: str | None

    execution_error: str | None

    # =====================================================
    # Jira Issue Retrieval
    # =====================================================

    issue_key: str | None