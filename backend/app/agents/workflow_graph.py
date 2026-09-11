from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.agents.state import AgentState

from app.agents.planner_agent import (
    planner_agent
)

from app.agents.plan_executor import (
    plan_executor
)

from app.agents.reasoning_agent import (
    reasoning_agent
)

from app.agents.workflow_agent import (
    workflow_agent
)

from app.agents.observation_agent import (
    observation_agent
)

from app.agents.supervisor import (
    supervisor,
    supervisor_router
)

def plan_executor_router(state: AgentState):
    """
    Backward-compatible router for existing tests/code.

    The actual orchestration is now handled by
    supervisor_router().
    """

    decision = supervisor_router(state)

    if decision == "reasoning":
        return "analysis"

    return decision

def observation_router(state: AgentState):
    """
    Backward-compatible router for existing tests/code.

    Actual orchestration is now handled by the Supervisor.
    This preserves the previous observation routing behavior.
    """

    execution_status = state.get(
        "execution_status"
    )

    if execution_status == "awaiting_human_approval":
        return "stop"

    if execution_status in (
        "terminated",
        "failed"
    ):
        return "stop"

    if execution_status == "completed":
        return "stop"

    if state.get(
        "goal_completed",
        False
    ):
        return "stop"

    if state.get(
        "self_correction_attempts",
        0
    ) >= 1:
        return "stop"

    return "continue"


graph_builder = StateGraph(
    AgentState
)


# =========================================================
# AGENTS
# =========================================================

graph_builder.add_node(
    "planner_agent",
    planner_agent
)

graph_builder.add_node(
    "plan_executor",
    plan_executor
)

graph_builder.add_node(
    "supervisor",
    supervisor
)

graph_builder.add_node(
    "reasoning_agent",
    reasoning_agent
)

graph_builder.add_node(
    "workflow_agent",
    workflow_agent
)

graph_builder.add_node(
    "observation_agent",
    observation_agent
)


# =========================================================
# START
# =========================================================

graph_builder.add_edge(
    START,
    "planner_agent"
)


# =========================================================
# PLANNER → EXECUTOR
# =========================================================

graph_builder.add_edge(
    "planner_agent",
    "plan_executor"
)


# =========================================================
# EXECUTOR → SUPERVISOR
# =========================================================

graph_builder.add_edge(
    "plan_executor",
    "supervisor"
)


# =========================================================
# SUPERVISOR ROUTING
# =========================================================

graph_builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "continue": "plan_executor",
        "reasoning": "reasoning_agent",
        "stop": END
    }
)


# =========================================================
# REASONING
# =========================================================

graph_builder.add_edge(
    "reasoning_agent",
    "workflow_agent"
)


# =========================================================
# WORKFLOW ANALYSIS
# =========================================================

graph_builder.add_edge(
    "workflow_agent",
    "observation_agent"
)


# =========================================================
# OBSERVATION → SUPERVISOR
# =========================================================

graph_builder.add_edge(
    "observation_agent",
    "supervisor"
)


# =========================================================
# COMPILE
# =========================================================

workflow_graph = graph_builder.compile()