import logging


logger = logging.getLogger(__name__)


def planner_agent(state):
    """
    Creates a decomposed execution plan
    from the detected user intent and goal.

    Planner decides WHAT needs to be done.

    It does not execute the tasks.
    """

    logger.info(
        "AGENT START | planner_agent"
    )

    intent = state.get(
        "intent"
    )

    user_goal = state.get(
        "user_goal"
    )

    plan = []

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
            "generate_recommendation"
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

    logger.info(
        "PLAN CREATED | intent=%s | steps=%s",
        intent,
        len(plan)
    )

    logger.info(
        "TASK DECOMPOSITION | plan=%s",
        plan
    )

    return {
        "user_goal": user_goal,
        "intent": intent,
        "plan": plan,
        "current_step": 0
    }