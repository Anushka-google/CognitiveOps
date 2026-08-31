from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.agents.state import (
    AgentState
)

from app.agents.planner_agent import (
    planner_agent
)

from app.agents.plan_executor import (
    plan_executor
)

from app.agents.observation_agent import (
    observation_agent
)


# =====================================================
# Graph Builder
# =====================================================

graph_builder = StateGraph(
    AgentState
)


# =====================================================
# Planner Node
# =====================================================

graph_builder.add_node(
    "planner_agent",
    planner_agent
)


# =====================================================
# Plan Executor Node
# =====================================================

graph_builder.add_node(
    "plan_executor",
    plan_executor
)


# =====================================================
# Observation Node
# =====================================================

graph_builder.add_node(
    "observation_agent",
    observation_agent
)


# =====================================================
# START → PLANNER
# =====================================================

graph_builder.add_edge(
    START,
    "planner_agent"
)


# =====================================================
# PLANNER → EXECUTOR
# =====================================================

graph_builder.add_edge(
    "planner_agent",
    "plan_executor"
)


# =====================================================
# EXECUTOR → OBSERVATION
# =====================================================

graph_builder.add_edge(
    "plan_executor",
    "observation_agent"
)


# =====================================================
# Observation Router
# =====================================================

def observation_router(
    state: AgentState
):

    # =================================================
    # Read Execution Status
    # =================================================

    execution_status = state.get(
        "execution_status",
        None
    )

    # =================================================
    # HUMAN-IN-THE-LOOP
    # =================================================

    if execution_status == (
        "awaiting_human_approval"
    ):

        return "stop"

    # =================================================
    # HARD TERMINATION
    # =================================================

    if execution_status in (
        "terminated",
        "failed"
    ):

        return "stop"

    # =================================================
    # GOAL COMPLETED
    # =================================================

    if (
        execution_status == "completed"
        or
        state.get(
            "goal_completed",
            False
        )
    ):

        return "stop"

    # =================================================
    # Observation
    # =================================================

    observation = state.get(
        "observation",
        {}
    )

    sufficient = observation.get(
        "sufficient",
        False
    )

    # =================================================
    # Sufficient Evidence
    # =================================================

    if sufficient:

        return "stop"

    # =================================================
    # Self-Correction Limit
    # =================================================

    self_correction_attempts = state.get(
        "self_correction_attempts",
        0
    )

    if self_correction_attempts >= 1:

        return "stop"

    # =================================================
    # Otherwise Continue
    # =================================================

    return "continue"


# =====================================================
# Conditional Graph Edges
# =====================================================

graph_builder.add_conditional_edges(

    "observation_agent",

    observation_router,

    {

        "stop": END,

        "continue": "plan_executor"
    }
)


# =====================================================
# Compile
# =====================================================

workflow_graph = (
    graph_builder.compile()
)