import time
import json

from datetime import datetime

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

        print(
            "=================================="
        )

        print(
            "WORKFLOW GRAPH SERVICE"
        )

        print(
            "=================================="
        )

        # --------------------------------
        # Start execution timer
        # --------------------------------

        start_time = time.perf_counter()

        # --------------------------------
        # Database session
        # --------------------------------

        db = SessionLocal()

        try:

            # =================================
            # Long-Term Memory
            # Retrieve previous executions
            # =================================

            previous_executions = (
                db.query(
                    WorkflowExecution
                )
                .order_by(
                    WorkflowExecution.id.desc()
                )
                .limit(5)
                .all()
            )

            long_term_memory = []

            for execution in previous_executions:

                if execution.memory:

                    long_term_memory.append(
                        execution.memory
                    )

            print(
                "LONG-TERM MEMORY | "
                "RETRIEVED | "
                f"count={len(long_term_memory)}"
            )

            # --------------------------------
            # Initial LangGraph state
            # --------------------------------

            initial_state = {

                # =================================
                # Core Workflow Data
                # =================================

                "workflows": workflows,

                "insights": [],

                # =================================
                # User / Intent
                # =================================

                "user_goal": (
                    "Analyze the workflow for "
                    "delays, bottlenecks, blockers, "
                    "and operational risks."
                ),

                "intent": "analyze_workflow",

                # =================================
                # Planner
                # =================================

                "plan": [],

                "current_step": 0,

                # =================================
                # Shared Agent State
                # =================================

                "tool_results": {},

                "evidence": {},

                "agent_outputs": {},

                "errors": [],

                "final_answer": None,

                # =================================
                # Long-Term Memory
                # =================================

                "long_term_memory": (
                    long_term_memory
                ),

                # =================================
                # Workflow Analysis
                # =================================

                "workflow_summary": None,

                "workflow_health": None,

                "total_issues": 0,

                "high_severity_issues": 0,

                "delayed_workflows": [],

                # =================================
                # Evidence
                # =================================

                "jira_evidence": [],

                "slack_evidence": [],

                "combined_evidence": {},

                # =================================
                # Observation
                # =================================

                "observation": {},

                "observations": [],

                # =================================
                # Termination Control
                # =================================

                "iteration_count": 0,

                "goal_completed": False,

                "no_useful_action": False,

                "termination_reason": None,

                # =================================
                # Execution
                # =================================

                "execution_status": None,

                "execution_error": None,

                # =================================
                # Jira Issue Retrieval
                # =================================

                "issue_key": None
            }

            print(
                "LONG-TERM MEMORY | "
                "AVAILABLE TO WORKFLOW"
            )

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

            # =================================
            # Create Long-Term Memory Snapshot
            # =================================

            memory_snapshot = {

                "workflow_health": (
                    result.get(
                        "workflow_health"
                    )
                ),

                "total_issues": (
                    result.get(
                        "total_issues",
                        0
                    )
                ),

                "high_severity_issues": (
                    result.get(
                        "high_severity_issues",
                        0
                    )
                ),

                "insights": (
                    result.get(
                        "insights",
                        []
                    )
                ),

                "execution_time": (
                    execution_time
                ),

                "created_at": (
                    datetime.utcnow()
                    .isoformat()
                )
            }

            memory_text = json.dumps(
                memory_snapshot,
                default=str
            )

            print(
                "LONG-TERM MEMORY | "
                "SNAPSHOT CREATED"
            )

            # --------------------------------
            # Save execution to database
            # --------------------------------

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

                execution_time=(
                    execution_time
                ),

                completed_at=(
                    datetime.utcnow()
                ),

                memory=(
                    memory_text
                )
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

            print(
                "LONG-TERM MEMORY | "
                f"SAVED | execution_id="
                f"{execution.id}"
            )

            return result

        except Exception as e:

            db.rollback()

            print(
                "DATABASE SAVE ERROR:",
                e
            )

            raise

        finally:

            db.close()