import logging
import time


logger = logging.getLogger(__name__)


def planner_agent(state):

    """
    Creates a decomposed execution plan
    from the detected user intent and goal.

    Planner decides WHAT needs to be done.

    Planner does NOT execute external actions.

    For high-impact actions, the planner adds
    a proposal step to the plan.

    The actual human approval gate is handled
    by plan_executor after the required evidence
    has been collected.
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

        plan = []

        # =====================================================
        # HUMAN-IN-THE-LOOP DEFAULTS
        # =====================================================

        proposed_action = {}

        approval_required = False

        approval_status = None

        approval_reason = None

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

                # =============================================
                # HUMAN-IN-THE-LOOP STEP
                # =============================================

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
            "HUMAN-IN-THE-LOOP | "
            "required=%s | "
            "status=%s",
            approval_required,
            approval_status
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