import logging
import time

from app.services.risk_scoring_service import (
    RiskScoringService
)


logger = logging.getLogger(__name__)


def planner_agent(state):

    """
    Creates a decomposed execution plan
    from the detected user intent and goal.

    Planner decides WHAT needs to be done.

    Planner does NOT execute external actions.

    For high-risk workflows, the planner adds
    a human-in-the-loop Jira proposal step.

    The actual approval gate is handled by
    plan_executor.
    """

    logger.info(
        "AGENT START | planner_agent"
    )

    start_time = time.perf_counter()

    try:

        intent = state.get(
            "intent"
        )

        user_goal = state.get(
            "user_goal"
        )

        workflows = state.get(
            "workflows",
            []
        )

        plan = []

        # =====================================================
        # HUMAN-IN-THE-LOOP DEFAULTS
        # =====================================================

        proposed_action = {}

        approval_required = False

        approval_status = None

        approval_reason = None

        issue_key = state.get(
            "issue_key"
        )

        # =====================================================
        # RISK ANALYSIS
        #
        # Planner uses the same deterministic risk service
        # used by the /api/risk endpoint.
        # =====================================================

        risk_data = {
            "average_risk": 0,
            "high_risk_tickets": 0,
            "tickets": []
        }

        try:

            risk_service = (
                RiskScoringService()
            )

            risk_data = (
                risk_service.calculate(
                    workflows
                )
            )

        except Exception as risk_error:

            logger.exception(
                "PLANNER RISK ANALYSIS FAILED | %s",
                risk_error
            )

        high_risk_tickets = [

            ticket

            for ticket in risk_data.get(
                "tickets",
                []
            )

            if ticket.get(
                "risk_level"
            ) == "High"

        ]

        # =====================================================
        # SELECT HIGHEST-RISK TICKET
        # =====================================================

        highest_risk_ticket = None

        if high_risk_tickets:

            highest_risk_ticket = max(
                high_risk_tickets,
                key=lambda item: item.get(
                    "risk_score",
                    0
                )
            )

            issue_key = (
                highest_risk_ticket.get(
                    "ticket_id"
                )
            )

            logger.warning(
                "HIGH-RISK TICKET DETECTED | "
                "ticket=%s | score=%s",
                issue_key,
                highest_risk_ticket.get(
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

                "identify_root_cause",

                "generate_recommendation"

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

            # =================================================
            # HIGH-RISK HUMAN-IN-THE-LOOP
            #
            # If at least one Jira ticket is High risk,
            # add the approval proposal as the final step.
            # =================================================

            if highest_risk_ticket:

                plan.append(
                    "propose_jira_change"
                )

                logger.warning(
                    "HITL STEP ADDED | "
                    "ticket=%s | "
                    "risk=%s",
                    issue_key,
                    highest_risk_ticket.get(
                        "risk_score"
                    )
                )

        # =====================================================
        # FIND BOTTLENECK
        # =====================================================

        elif intent == "find_bottleneck":

            plan = [

                "find_workflow",

                "find_delayed_tasks",

                "detect_delays",

                "retrieve_jira_evidence",

                "retrieve_slack_evidence",

                "compare_evidence",

                "observe",

                "identify_bottlenecks"

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

                "identify_root_cause",

                "generate_recommendation",

                "propose_jira_change"

            ]

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
        # Execution Time
        # =====================================================

        execution_time = (
            time.perf_counter()
            - start_time
        )

        # =====================================================
        # Logging
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

        logger.info(
            "RISK SUMMARY | average=%s | high_risk=%s",
            risk_data.get(
                "average_risk"
            ),
            risk_data.get(
                "high_risk_tickets"
            )
        )

        logger.info(
            "HUMAN-IN-THE-LOOP | "
            "required=%s | "
            "status=%s | "
            "issue=%s",
            approval_required,
            approval_status,
            issue_key
        )

        # =====================================================
        # Structured Agent Output
        # =====================================================

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        agent_outputs[
            "planner_agent"
        ] = {

            "agent": "planner_agent",

            "status": "success",

            "output": {

                "intent": intent,

                "plan": plan,

                "steps": len(plan),

                "issue_key": issue_key,

                "risk_data": risk_data,

                "high_risk_ticket": (
                    highest_risk_ticket
                ),

                "proposed_action": (
                    proposed_action
                ),

                "approval_required": (
                    approval_required
                ),

                "approval_status": (
                    approval_status
                )

            },

            "execution_time": (
                execution_time
            ),

            "error": None

        }

        logger.info(
            "STRUCTURED OUTPUT | "
            "agent=planner_agent | "
            "status=success"
        )

        logger.info(
            "AGENT END | planner_agent"
        )

        # =====================================================
        # State Update
        # =====================================================

        return {

            "user_goal": user_goal,

            "intent": intent,

            "plan": plan,

            "current_step": 0,

            "issue_key": issue_key,

            "proposed_action": (
                proposed_action
            ),

            "approval_required": (
                approval_required
            ),

            "approval_status": (
                approval_status
            ),

            "approval_reason": (
                approval_reason
            ),

            "agent_outputs": (
                agent_outputs
            )

        }

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

        agent_outputs[
            "planner_agent"
        ] = {

            "agent": "planner_agent",

            "status": "failed",

            "output": None,

            "execution_time": (
                execution_time
            ),

            "error": str(e)

        }

        return {

            "agent_outputs": (
                agent_outputs
            ),

            "errors": [
                str(e)
            ],

            "execution_status": (
                "failed"
            ),

            "execution_error": (
                str(e)
            )

        }