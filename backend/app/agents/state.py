from typing import (
    Any,
    TypedDict
)


# =====================================================
# Structured Agent Output
# =====================================================

class AgentOutput(TypedDict, total=False):

    status: str

    result: Any

    error: str | None


# =====================================================
# Agent State
# =====================================================

class AgentState(TypedDict, total=False):

    # =========================================
    # Core Workflow Data
    # =========================================

    workflows: list[Any]

    insights: list[Any]

    workflow_summary: Any

    workflow_health: Any

    total_issues: int

    high_severity_issues: int

    delayed_workflows: list[Any]

    # =========================================
    # User / Intent
    # =========================================

    user_goal: str

    intent: str

    # =========================================
    # Planner
    # =========================================

    plan: list[str]

    current_step: int

    # =========================================
    # Agent Memory
    # =========================================

    tool_results: dict[str, Any]

    evidence: dict[str, Any]

    agent_outputs: dict[str, AgentOutput]

    errors: list[Any]

    final_answer: Any

    # =========================================
    # Evidence
    # =========================================

    jira_evidence: list[Any]

    slack_evidence: list[Any]

    combined_evidence: dict[str, Any]

    issue_key: str | None

    # =========================================
    # Observation
    # =========================================

    observation: dict[str, Any]

    observations: list[Any]

    # =========================================
    # Execution
    # =========================================

    execution_status: str | None

    execution_error: str | None

    # =========================================
    # Long-Term Memory
    # =========================================

    long_term_memory: list[Any]

    # =========================================
    # Self-Correction
    # =========================================

    self_correction_attempts: int

    self_correction_required: bool

    # =========================================
    # TERMINATION CONTROL
    # =========================================

    goal_completed: bool

    termination_reason: str | None

    iteration_count: int

    # -----------------------------------------
    # Tracks whether the same plan step is
    # being executed repeatedly.
    # -----------------------------------------

    last_step: str | None

    step_repeat_count: int

    # =========================================
    # HUMAN-IN-THE-LOOP
    # =========================================

    proposed_action: dict[str, Any]

    approval_required: bool

    approval_status: str | None

    approval_reason: str | None