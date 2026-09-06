from langgraph.graph import StateGraph, START, END

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


graph_builder = StateGraph(AgentState)


# --------------------------------------------------
# Nodes
# --------------------------------------------------

graph_builder.add_node(
    "planner_agent",
    planner_agent
)

graph_builder.add_node(
    "plan_executor",
    plan_executor
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


# --------------------------------------------------
# Initial flow
# --------------------------------------------------

graph_builder.add_edge(
    START,
    "planner_agent"
)

graph_builder.add_edge(
    "planner_agent",
    "plan_executor"
)


# --------------------------------------------------
# Plan Executor Router
# --------------------------------------------------

def plan_executor_router(state: AgentState):

    execution_status = state.get(
        "execution_status"
    )

    current_step = state.get(
        "current_step",
        0
    )

    reasoning_completed = state.get(
        "reasoning_completed",
        False
    )


    # --------------------------------------------------
    # HITL / failure states
    # --------------------------------------------------

    if execution_status == "awaiting_human_approval":
        return "stop"


    if execution_status in (
        "terminated",
        "failed"
    ):
        return "stop"


    # --------------------------------------------------
    # Completed execution
    # --------------------------------------------------

    if execution_status == "completed":
        return "stop"


    if state.get(
        "goal_completed",
        False
    ):
        return "stop"


    # --------------------------------------------------
    # IMPORTANT:
    # Run reasoning after evidence/pattern
    # collection and before recommendations.
    #
    # Current plan:
    #
    # 0 find_workflow
    # 1 detect_patterns
    # 2 find_delayed_tasks
    # 3 retrieve_jira_evidence
    # 4 retrieve_slack_evidence
    # 5 compare_evidence
    # 6 observe
    # 7 root_cause
    # 8 generate_recommendations
    # 9 propose_jira_change
    #
    # Therefore when current_step reaches 8,
    # reasoning must happen first.
    # --------------------------------------------------

    if (
        current_step >= 8
        and not reasoning_completed
    ):
        return "analysis"


    # --------------------------------------------------
    # Normal plan continuation
    # --------------------------------------------------

    plan = state.get(
        "plan"
    ) or []


    if plan:

        try:

            if current_step >= len(plan):
                return "analysis"

        except TypeError:

            pass


    return "continue"


# --------------------------------------------------
# Plan Executor Conditional Edges
# --------------------------------------------------

graph_builder.add_conditional_edges(
    "plan_executor",

    plan_executor_router,

    {
        "continue": "plan_executor",

        "analysis": "reasoning_agent",

        "stop": END
    }
)


# --------------------------------------------------
# Intelligence / Analysis flow
# --------------------------------------------------

graph_builder.add_edge(
    "reasoning_agent",
    "workflow_agent"
)


graph_builder.add_edge(
    "workflow_agent",
    "observation_agent"
)


# --------------------------------------------------
# Observation Router
# --------------------------------------------------

def observation_router(state: AgentState):

    execution_status = state.get(
        "execution_status"
    )


    # --------------------------------------------------
    # HITL
    # --------------------------------------------------

    if execution_status == "awaiting_human_approval":
        return "stop"


    # --------------------------------------------------
    # Failure / termination
    # --------------------------------------------------

    if execution_status in (
        "terminated",
        "failed"
    ):
        return "stop"


    # --------------------------------------------------
    # Completed
    # --------------------------------------------------

    if execution_status == "completed":
        return "stop"


    if state.get(
        "goal_completed",
        False
    ):
        return "stop"


    # --------------------------------------------------
    # Self-correction protection
    # --------------------------------------------------

    if state.get(
        "self_correction_attempts",
        0
    ) >= 1:
        return "stop"


    # --------------------------------------------------
    # Continue plan execution
    # --------------------------------------------------

    return "continue"


# --------------------------------------------------
# Observation Conditional Edges
# --------------------------------------------------

graph_builder.add_conditional_edges(
    "observation_agent",

    observation_router,

    {
        "stop": END,

        "continue": "plan_executor"
    }
)


# --------------------------------------------------
# Compile Graph
# --------------------------------------------------

workflow_graph = graph_builder.compile()