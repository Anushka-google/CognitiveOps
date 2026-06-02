from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph import END

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
graph_builder.add_edge(
    START,
    "pattern_agent",
)

graph_builder.add_edge(
    "pattern_agent","reasoning_agent",
)

graph_builder.add_edge(
    "reasoning_agent", END
)

workflow_graph = (
    graph_builder.compile()
)