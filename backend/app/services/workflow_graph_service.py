from app.agents.workflow_graph import (
    workflow_graph
)


class WorkflowGraphService:

    def analyze(
        self,
        workflows
    ):

        initial_state = {
            "workflows": workflows,
            "insights": [],
            "workflow_summary": None,
            "workflow_health": None,
            "total_issues": 0,
            "high_severity_issues": 0
        }

        return workflow_graph.invoke(
            initial_state
        )