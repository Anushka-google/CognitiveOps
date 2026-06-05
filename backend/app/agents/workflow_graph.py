from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph import END
from app.agents.state import AgentState
from app.agents.router import (
    route_after_pattern
)
from app.agents.workflow_agent import (
    workflow_agent
)

from app.agents.recommendation_agent import(
    recommendation_agent
)

from app.agents.state import AgentState


from app.agents.pattern_agent import pattern_agent
from app.agents.reasoning_agent import (
    reasoning_agent
)

graph_builder = StateGraph(
    AgentState
)
graph_builder.add_node(
    "pattern_agent",
    pattern_agent
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
    "recommendation_agent",
    recommendation_agent
)
graph_builder.add_edge(
    START,
    "pattern_agent",
)

graph_builder.add_conditional_edges(
    "pattern_agent",
    route_after_pattern,
    {
        "workflow_agent":
            "workflow_agent",

        "end":
            END
    }
)

graph_builder.add_edge(
    "workflow_agent",
    "reasoning_agent"
)

graph_builder.add_edge(
    "reasoning_agent",
    "recommendation_agent"
)

graph_builder.add_edge(
    "recommendation_agent",
    END
)

workflow_graph = (
    graph_builder.compile()
)