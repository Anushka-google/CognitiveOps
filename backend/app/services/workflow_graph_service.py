import time
import json
import logging

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

from app.services.trace_service import (
    set_execution_id,
    trace_log,
    clear_trace_context
)


logger = logging.getLogger(__name__)


class WorkflowGraphService:

    def analyze(
        self,
        workflows
    ):

        logger.info(
            "WORKFLOW GRAPH SERVICE START"
        )

        start_time = (
            time.perf_counter()
        )

        db = SessionLocal()

        execution = None

        try:

            # =================================================
            # CREATE EXECUTION RECORD FIRST
            # =================================================

            execution = WorkflowExecution(

                started_at=
                    datetime.utcnow(),

                total_issues=
                    0,

                high_severity_issues=
                    0,

                workflow_health=
                    None,

                memory=
                    None
            )

            db.add(
                execution
            )

            # -------------------------------------------------
            # Flush creates the DB row and assigns its ID
            # without committing the transaction.
            # -------------------------------------------------

            db.flush()

            execution_id = (
                execution.id
            )

            # =================================================
            # SET TRACE CONTEXT
            # =================================================

            set_execution_id(
                execution_id
            )

            trace_log(
                "EXECUTION_START",
                (
                    f"workflow_count="
                    f"{len(workflows)}"
                )
            )

            logger.info(
                "EXECUTION CREATED | "
                "execution_id=%s",
                execution_id
            )

            # =================================================
            # LONG-TERM MEMORY
            # =================================================

            previous_executions = (

                db.query(
                    WorkflowExecution
                )

                .filter(
                    WorkflowExecution.id
                    != execution_id
                )

                .order_by(
                    WorkflowExecution.id.desc()
                )

                .limit(
                    5
                )

                .all()
            )

            long_term_memory = []

            for previous_execution in (
                previous_executions
            ):

                if previous_execution.memory:

                    long_term_memory.append(
                        previous_execution.memory
                    )

            logger.info(
                "LONG-TERM MEMORY | "
                "RETRIEVED | count=%s",
                len(long_term_memory)
            )

            trace_log(
                "LONG_TERM_MEMORY_RETRIEVED",
                (
                    f"count={len(long_term_memory)}"
                )
            )

            # =================================================
            # INITIAL LANGGRAPH STATE
            # =================================================

            initial_state = {

                # ---------------------------------------------
                # Execution identity
                # ---------------------------------------------

                "execution_id":
                    execution_id,

                # ---------------------------------------------
                # Core Workflow Data
                # ---------------------------------------------

                "workflows":
                    workflows,

                "insights":
                    [],

                # ---------------------------------------------
                # User / Intent
                # ---------------------------------------------

                "user_goal":
                    (
                        "Analyze the workflow for "
                        "delays, bottlenecks, blockers, "
                        "and operational risks."
                    ),

                "intent":
                    "analyze_workflow",

                # ---------------------------------------------
                # Planner
                # ---------------------------------------------

                "plan":
                    [],

                "current_step":
                    0,

                # ---------------------------------------------
                # HITL
                # ---------------------------------------------

                "proposed_action":
                    {},

                "approval_required":
                    False,

                "approval_status":
                    None,

                "approval_reason":
                    None,

                # ---------------------------------------------
                # Shared State
                # ---------------------------------------------

                "tool_results":
                    {},

                "evidence":
                    {},

                "agent_outputs":
                    {},

                "errors":
                    [],

                "final_answer":
                    None,

                # ---------------------------------------------
                # Long-Term Memory
                # ---------------------------------------------

                "long_term_memory":
                    long_term_memory,

                # ---------------------------------------------
                # Workflow Analysis
                # ---------------------------------------------

                "workflow_summary":
                    None,

                "workflow_health":
                    None,

                "total_issues":
                    0,

                "high_severity_issues":
                    0,

                "delayed_workflows":
                    [],

                # ---------------------------------------------
                # Evidence
                # ---------------------------------------------

                "jira_evidence":
                    [],

                "slack_evidence":
                    [],

                "combined_evidence":
                    {},

                # ---------------------------------------------
                # Observation
                # ---------------------------------------------

                "observation":
                    {},

                "observations":
                    [],

                "self_correction_required":
                    False,

                "self_correction_attempts":
                    0,

                # ---------------------------------------------
                # Termination
                # ---------------------------------------------

                "iteration_count":
                    0,

                "goal_completed":
                    False,

                "no_useful_action":
                    False,

                "termination_reason":
                    None,

                # ---------------------------------------------
                # Execution
                # ---------------------------------------------

                "execution_status":
                    None,

                "execution_error":
                    None,

                # ---------------------------------------------
                # Jira
                # ---------------------------------------------

                "issue_key":
                    None
            }

            trace_log(
                "LANGGRAPH_START"
            )

            # =================================================
            # EXECUTE LANGGRAPH
            # =================================================

            result = (
                workflow_graph.invoke(
                    initial_state
                )
            )

            trace_log(
                "LANGGRAPH_END"
            )

            # =================================================
            # EXECUTION TIME
            # =================================================

            execution_time = (

                time.perf_counter()
                - start_time
            )

            logger.info(
                "WORKFLOW EXECUTION TIME | %.2fs",
                execution_time
            )

            # =================================================
            # HITL STATE
            # =================================================

            execution_status = (
                result.get(
                    "execution_status"
                )
            )

            approval_required = (
                result.get(
                    "approval_required"
                )
            )

            approval_status = (
                result.get(
                    "approval_status"
                )
            )

            proposed_action = (
                result.get(
                    "proposed_action"
                )
            )

            logger.info(
                "HITL STATE | "
                "approval_required=%s | "
                "approval_status=%s | "
                "execution_status=%s",

                approval_required,

                approval_status,

                execution_status
            )

            trace_log(
                "HITL_STATE",
                (
                    f"approval_required={approval_required} "
                    f"approval_status={approval_status} "
                    f"execution_status={execution_status}"
                )
            )

            # =================================================
            # COMPLETION
            # =================================================

            if (
                execution_status
                ==
                "awaiting_human_approval"
            ):

                completed_at = None

            else:

                completed_at = (
                    datetime.utcnow()
                )

            # =================================================
            # MEMORY SNAPSHOT
            # =================================================

            memory_snapshot = {

                "workflow_health":
                    result.get(
                        "workflow_health"
                    ),

                "total_issues":
                    result.get(
                        "total_issues",
                        0
                    ),

                "high_severity_issues":
                    result.get(
                        "high_severity_issues",
                        0
                    ),

                "insights":
                    result.get(
                        "insights",
                        []
                    ),

                "execution_id":
                    execution_id,

                "execution_time":
                    execution_time,

                "created_at":
                    datetime.utcnow()
                    .isoformat(),

                "issue_key":
                    result.get(
                        "issue_key"
                    ),

                "proposed_action":
                    result.get(
                        "proposed_action",
                        {}
                    ),

                "approval_required":
                    result.get(
                        "approval_required",
                        False
                    ),

                "approval_status":
                    result.get(
                        "approval_status"
                    ),

                "approval_reason":
                    result.get(
                        "approval_reason"
                    ),

                "execution_status":
                    result.get(
                        "execution_status"
                    ),

                "execution_error":
                    result.get(
                        "execution_error"
                    ),

                "goal_completed":
                    result.get(
                        "goal_completed",
                        False
                    ),

                "termination_reason":
                    result.get(
                        "termination_reason"
                    ),

                "approved_at":
                    result.get(
                        "approved_at"
                    ),

                "rejected_at":
                    result.get(
                        "rejected_at"
                    ),

                "approved_action_result":
                    result.get(
                        "approved_action_result"
                    )
            }

            memory_text = json.dumps(
                memory_snapshot,
                default=str
            )

            # =================================================
            # UPDATE EXISTING EXECUTION
            # =================================================

            execution.workflow_health = (
                result.get(
                    "workflow_health"
                )
            )

            execution.total_issues = (
                result.get(
                    "total_issues",
                    0
                )
            )

            execution.high_severity_issues = (
                result.get(
                    "high_severity_issues",
                    0
                )
            )

            execution.execution_time = (
                execution_time
            )

            execution.completed_at = (
                completed_at
            )

            execution.memory = (
                memory_text
            )

            # =================================================
            # COMMIT
            # =================================================

            db.commit()

            db.refresh(
                execution
            )

            # =================================================
            # FINAL TRACE
            # =================================================

            trace_log(
                "EXECUTION_END",
                (
                    f"status={execution_status} "
                    f"execution_time={execution_time:.2f}s"
                )
            )

            logger.info(
                "WORKFLOW EXECUTION SAVED | "
                "execution_id=%s",

                execution.id
            )

            # =================================================
            # RETURN EXECUTION ID
            # =================================================

            result = dict(
                result
            )

            result[
                "execution_id"
            ] = execution.id

            return result

        except Exception as e:

            db.rollback()

            logger.exception(
                "WORKFLOW EXECUTION FAILED | %s",
                e
            )

            trace_log(
                "EXECUTION_FAILED",
                str(e),
                logging.ERROR
            )

            raise

        finally:

            db.close()

            clear_trace_context()

            logger.info(
                "WORKFLOW GRAPH SERVICE END"
            )