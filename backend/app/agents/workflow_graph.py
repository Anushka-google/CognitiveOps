from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.planner_agent import planner_agent
from app.agents.plan_executor import plan_executor
from app.agents.workflow_agent import workflow_agent
from app.agents.observation_agent import observation_agent


# =========================================================
# GRAPH BUILDER
# =========================================================

graph_builder = StateGraph(AgentState)


# =========================================================
# NODES
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
    "workflow_agent",
    workflow_agent
)

graph_builder.add_node(
    "observation_agent",
    observation_agent
)


# =========================================================
# INITIAL FLOW
# =========================================================

graph_builder.add_edge(
    START,
    "planner_agent"
)

graph_builder.add_edge(
    "planner_agent",
    "plan_executor"
)


# =========================================================
# PLAN EXECUTION → WORKFLOW ANALYSIS
# =========================================================

graph_builder.add_edge(
    "plan_executor",
    "workflow_agent"
)

graph_builder.add_edge(
    "workflow_agent",
    "observation_agent"
)


# =========================================================
# OBSERVATION ROUTER
# =========================================================

def observation_router(
    state: AgentState
):

    execution_status = state.get(
        "execution_status"
    )

    # =====================================================
    # HITL STOP
    # =====================================================

    if execution_status == (
        "awaiting_human_approval"
    ):

        return "stop"


    # =====================================================
    # FAILED / TERMINATED
    # =====================================================

    if execution_status in (
        "terminated",
        "failed"
    ):

        return "stop"


    # =====================================================
    # COMPLETED
    # =====================================================

    if execution_status == "completed":

        return "stop"


    # =====================================================
    # GOAL COMPLETED
    # =====================================================

    if state.get(
        "goal_completed",
        False
    ):

        return "stop"


    # =====================================================
    # SELF-CORRECTION LIMIT
    # =====================================================

    if (
        state.get(
            "self_correction_attempts",
            0
        )
        >= 1
    ):

        return "stop"


    # =====================================================
    # CONTINUE PLAN
    # =====================================================

    return "continue"


# =========================================================
# CONDITIONAL FLOW
# =========================================================

graph_builder.add_conditional_edges(

    "observation_agent",

    observation_router,

    {
        "stop": END,

        "continue": "plan_executor"
    }
)


# =========================================================
# COMPILE GRAPH
# =========================================================

workflow_graph = (
    graph_builder.compile()
)