from typing import Any, TypedDict


class AgentOutput(TypedDict, total=False):
    status: str
    result: Any
    error: str | None


class AgentState(TypedDict, total=False):
    workflows: list[Any]

    insights: list[Any]

    workflow_summary: Any

    workflow_health: Any

    total_issues: int

    high_severity_issues: int

    delayed_workflows: list[Any]

    user_goal: str

    intent: str

    plan: list[str]

    current_step: int

    tool_results: dict[str, Any]

    evidence: dict[str, Any]

    agent_outputs: dict[str, AgentOutput]

    errors: list[Any]

    final_answer: Any

    jira_evidence: list[Any]

    slack_evidence: list[Any]

    combined_evidence: dict[str, Any]

    issue_key: str | None

    observation: dict[str, Any]

    observations: list[Any]

    execution_status: str | None

    execution_error: str | None

    long_term_memory: list[Any]

    self_correction_attempts: int

    self_correction_required: bool

    goal_completed: bool

    termination_reason: str | None

    iteration_count: int

    last_step: str | None

    step_repeat_count: int

    proposed_action: dict[str, Any]

    approval_required: bool

    approval_status: str | None

    approval_reason: str | None

    sla_prediction: dict[str, Any]

    root_cause_graph: dict[str, Any]

    # --------------------------------------------------
    # Phase 2.13 tracing / reasoning control
    # --------------------------------------------------
    reasoning_completed: bool

    # --------------------------------------------------
    # Phase 5.3 Executive Intelligence (#72)
    # --------------------------------------------------
    executive_summary: dict[str, Any]