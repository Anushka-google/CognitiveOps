import logging
import time

from app.agents.state import AgentState
from app.services.risk_scoring_service import RiskScoringService


logger = logging.getLogger(__name__)


def planner_agent(state: AgentState):
    """
    Creates a decomposed execution plan.

    Planner decides WHAT needs to be done.

    Planner does NOT:
    - execute Jira actions
    - mutate Jira
    - approve actions

    High-risk Jira actions are only proposed.
    Actual approval handling happens in plan_executor
    and the approval API.
    """

    logger.info("AGENT START | planner_agent")

    start_time = time.perf_counter()

    try:

        # =====================================================
        # READ STATE
        # =====================================================

        intent = state.get("intent")

        user_goal = state.get("user_goal")

        workflows = list(
            state.get("workflows", [])
        )

        existing_issue_key = state.get(
            "issue_key"
        )

        # =====================================================
        # DEFAULTS
        # =====================================================

        plan = []

        proposed_action = {}

        approval_required = False

        approval_status = None

        approval_reason = None

        issue_key = existing_issue_key

        # =====================================================
        # RISK ANALYSIS
        # =====================================================

        risk_data = {
            "average_risk": 0,
            "high_risk_tickets": [],
            "tickets": []
        }

        try:

            risk_service = RiskScoringService()

            risk_data = risk_service.calculate(
                workflows
            )

        except Exception as risk_error:

            logger.exception(
                "RISK ANALYSIS FAILED | %s",
                risk_error
            )

        # =====================================================
        # FIND HIGH-RISK TICKETS
        # =====================================================

        high_risk_tickets = [
            ticket
            for ticket in risk_data.get(
                "tickets",
                []
            )
            if ticket.get("risk_level") == "High"
        ]

        # =====================================================
        # SELECT HIGHEST-RISK TICKET
        #
        # IMPORTANT:
        # We select the ticket with the maximum risk score,
        # not simply the first High-risk ticket.
        # =====================================================

        selected_high_risk = None

        if high_risk_tickets:

            selected_high_risk = max(
                high_risk_tickets,
                key=lambda ticket: ticket.get(
                    "risk_score",
                    0
                )
            )

        # =====================================================
        # SET ISSUE KEY
        # =====================================================

        if selected_high_risk:

            selected_issue_key = (
                selected_high_risk.get(
                    "ticket_id"
                )
            )

            # If the planner already received a specific issue
            # key, preserve it. Otherwise select highest risk.
            if not issue_key:

                issue_key = selected_issue_key

            logger.info(
                "HIGH-RISK TICKET DETECTED | "
                "selected=%s | score=%s",
                issue_key,
                selected_high_risk.get(
                    "risk_score"
                )
            )

        # =====================================================
        # EXPLAIN DELAY
        # =====================================================

        if intent == "explain_delay":

            plan = [
                "find_workflow",
                "find_delayed_tasks",
                "retrieve_jira_evidence",
                "retrieve_slack_evidence",
                "compare_evidence",
                "observe",
                "identify_root_causes",
                "generate_recommendations"
            ]

        # =====================================================
        # ANALYZE WORKFLOW
        # =====================================================

        elif intent == "analyze_workflow":

            plan = [
                "find_workflow",
                "detect_patterns",
                "find_delayed_tasks",
                "retrieve_jira_evidence",
                "retrieve_slack_evidence",
                "compare_evidence",
                "observe",
                "identify_root_causes",
                "generate_recommendations"
            ]

            # -------------------------------------------------
            # Add HITL proposal only when a High-risk ticket
            # exists.
            # -------------------------------------------------

            if selected_high_risk:

                plan.append(
                    "propose_jira_change"
                )

        # =====================================================
        # FIND BOTTLENECK
        # =====================================================

        elif intent == "find_bottleneck":

            plan = [
                "find_workflow",
                "detect_patterns",
                "find_delayed_tasks",
                "retrieve_jira_evidence",
                "retrieve_slack_evidence",
                "compare_evidence",
                "observe",
                "identify_bottlenecks",
                "generate_recommendations"
            ]

        # =====================================================
        # RECOMMEND ACTION
        # =====================================================

        elif intent == "recommend_action":

            plan = [
                "find_workflow",
                "identify_problem",
                "retrieve_jira_evidence",
                "retrieve_slack_evidence",
                "compare_evidence",
                "observe",
                "identify_root_causes",
                "generate_recommendations"
            ]

            if selected_high_risk:

                plan.append(
                    "propose_jira_change"
                )

        # =====================================================
        # RETRIEVE JIRA ISSUE
        # =====================================================

        elif intent == "retrieve_jira_issue":

            plan = [
                "extract_issue_key",
                "retrieve_jira_issue",
                "return_issue"
            ]

        # =====================================================
        # UNKNOWN INTENT
        # =====================================================

        else:

            plan = [
                "understand_goal"
            ]

        # =====================================================
        # LOG PLAN
        # =====================================================

        logger.info(
            "PLAN CREATED | intent=%s | steps=%s",
            intent,
            len(plan)
        )

        logger.info(
            "TASK DECOMPOSITION | plan=%s",
            plan
        )

        # =====================================================
        # STRUCTURED OUTPUT
        # =====================================================

        execution_time = (
            time.perf_counter()
            - start_time
        )

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        agent_outputs["planner_agent"] = {

            "agent":
                "planner_agent",

            "status":
                "success",

            "output": {

                "intent":
                    intent,

                "plan":
                    plan,

                "steps":
                    len(plan),

                "high_risk_tickets":
                    high_risk_tickets,

                "selected_issue_key":
                    issue_key,

                "selected_risk_score":
                    (
                        selected_high_risk.get(
                            "risk_score"
                        )
                        if selected_high_risk
                        else None
                    ),

                "proposed_action":
                    proposed_action,

                "approval_required":
                    approval_required,

                "approval_status":
                    approval_status,

                "approval_reason":
                    approval_reason
            },

            "execution_time":
                execution_time,

            "error":
                None
        }

        # =====================================================
        # RETURN
        # =====================================================

        return {

            "user_goal":
                user_goal,

            "intent":
                intent,

            "plan":
                plan,

            "current_step":
                0,

            "issue_key":
                issue_key,

            "proposed_action":
                proposed_action,

            "approval_required":
                approval_required,

            "approval_status":
                approval_status,

            "approval_reason":
                approval_reason,

            "execution_status":
                None,

            "execution_error":
                None,

            "goal_completed":
                False,

            "termination_reason":
                None,

            "agent_outputs":
                agent_outputs
        }

    # =========================================================
    # ERROR
    # =========================================================

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | planner_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        agent_outputs["planner_agent"] = {

            "agent":
                "planner_agent",

            "status":
                "failed",

            "output":
                None,

            "execution_time":
                execution_time,

            "error":
                str(e)
        }

        errors = list(
            state.get(
                "errors",
                []
            )
        )

        errors.append({

            "agent":
                "planner_agent",

            "error":
                str(e)
        })

        return {

            "agent_outputs":
                agent_outputs,

            "errors":
                errors,

            "execution_status":
                "failed",

            "execution_error":
                str(e)
        }