import time

from app.agents.workflow_graph import (
    workflow_graph
)

from app.db.database import (
    SessionLocal
)

from app.models.execution import (
    WorkflowExecution
)


class WorkflowGraphService:

    def analyze(
        self,
        workflows
    ):

        print("==================================")
        print("WORKFLOW GRAPH SERVICE")
        print("==================================")

        # --------------------------------
        # Start execution timer
        # --------------------------------

        start_time = time.perf_counter()

        # --------------------------------
        # Initial LangGraph state
        # --------------------------------

        initial_state = {
            "workflows": workflows,
            "insights": [],
            "workflow_summary": None,
            "workflow_health": None,
            "total_issues": 0,
            "high_severity_issues": 0
        }

        # --------------------------------
        # Execute LangGraph workflow
        # --------------------------------

        result = workflow_graph.invoke(
            initial_state
        )

        # --------------------------------
        # Calculate execution time
        # --------------------------------

        execution_time = (
            time.perf_counter()
            - start_time
        )

        print(
            f"WORKFLOW EXECUTION TIME: "
            f"{execution_time:.2f}s"
        )

        # --------------------------------
        # Save execution to database
        # --------------------------------

        db = SessionLocal()

        try:

            execution = WorkflowExecution(
                workflow_health=(
                    result.get(
                        "workflow_health"
                    )
                ),
                total_issues=(
                    result.get(
                        "total_issues",
                        0
                    )
                ),
                high_severity_issues=(
                    result.get(
                        "high_severity_issues",
                        0
                    )
                ),
                execution_time=execution_time
            )

            db.add(
                execution
            )

            db.commit()

            db.refresh(
                execution
            )

            print(
                "WORKFLOW EXECUTION SAVED"
            )

            print(
                f"EXECUTION ID: "
                f"{execution.id}"
            )

        except Exception as e:

            db.rollback()

            print(
                "DATABASE SAVE ERROR:",
                e
            )

        finally:

            db.close()

        # --------------------------------
        # Return workflow result
        # --------------------------------

        return result