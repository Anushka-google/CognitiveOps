import logging

from app.agents.pattern_agent import (
    pattern_agent
)

from app.agents.reasoning_agent import (
    reasoning_agent
)

from app.agents.recommendation_agent import (
    recommendation_agent
)

from app.agents.observation_agent import (
    observation_agent
)

from app.services.slack_service import (
    SlackService
)


logger = logging.getLogger(__name__)


def observe_tool_result(
    state,
    tool_name,
    result_count,
    sufficient,
    details=None
):
    """
    Records the result of an executed tool/agent.

    Observation answers:
        What happened?
        How much result was produced?
        Is the result currently sufficient?
    """

    observation = {
        "tool": tool_name,
        "result_count": result_count,
        "sufficient": sufficient
    }

    if details:
        observation["details"] = details

    observations = state.setdefault(
        "observations",
        []
    )

    observations.append(
        observation
    )

    logger.info(
        "OBSERVATION | "
        "tool=%s | "
        "result_count=%s | "
        "sufficient=%s",
        tool_name,
        result_count,
        sufficient
    )

    return observation


def plan_executor(state):
    """
    Executes the plan created by planner_agent.

    Planner decides:
        WHAT should be done.

    Executor decides:
        WHICH step to execute next
        and passes the resulting state forward.

    Observation records:
        WHAT happened after each execution.

    Observation Agent decides:
        WHETHER the collected evidence
        is sufficient for reasoning.
    """

    logger.info(
        "PLAN EXECUTOR START"
    )

    plan = state.get(
        "plan",
        []
    )

    current_step = state.get(
        "current_step",
        0
    )

    state.setdefault(
        "observations",
        []
    )

    # --------------------------------
    # Validate plan
    # --------------------------------

    if not plan:

        logger.warning(
            "PLAN EXECUTOR | "
            "No plan available"
        )

        return state

    # --------------------------------
    # Execute plan
    # --------------------------------

    while current_step < len(plan):

        step = plan[current_step]

        logger.info(
            "PLAN STEP START | "
            "step=%s | index=%s",
            step,
            current_step
        )

        try:

            # =========================================
            # FIND WORKFLOW
            # =========================================

            if step == "find_workflow":

                logger.info(
                    "EXECUTING | find_workflow"
                )

                workflows = state.get(
                    "workflows",
                    []
                )

                sufficient = (
                    len(workflows) > 0
                )

                if not sufficient:

                    logger.warning(
                        "WORKFLOW NOT FOUND"
                    )

                    state[
                        "execution_status"
                    ] = "workflow_not_found"

                    observe_tool_result(
                        state,
                        "find_workflow",
                        len(workflows),
                        False
                    )

                    break

                observe_tool_result(
                    state,
                    "find_workflow",
                    len(workflows),
                    True
                )

            # =========================================
            # FIND DELAYED TASKS
            # =========================================

            elif step == "find_delayed_tasks":

                logger.info(
                    "EXECUTING | find_delayed_tasks"
                )

                workflows = state.get(
                    "workflows",
                    []
                )

                delayed_workflows = [
                    workflow
                    for workflow in workflows
                    if getattr(
                        workflow,
                        "days_waiting",
                        0
                    ) > 0
                ]

                state[
                    "delayed_workflows"
                ] = delayed_workflows

                logger.info(
                    "DELAYED WORKFLOWS FOUND | count=%s",
                    len(delayed_workflows)
                )

                observe_tool_result(
                    state,
                    "find_delayed_tasks",
                    len(delayed_workflows),
                    len(delayed_workflows) > 0
                )

            # =========================================
            # RETRIEVE JIRA EVIDENCE
            # =========================================

            elif step == "retrieve_jira_evidence":

                logger.info(
                    "EXECUTING | retrieve_jira_evidence"
                )

                delayed_workflows = state.get(
                    "delayed_workflows",
                    state.get(
                        "workflows",
                        []
                    )
                )

                jira_evidence = []

                for workflow in delayed_workflows:

                    jira_evidence.append({
                        "ticket_id": getattr(
                            workflow,
                            "ticket_id",
                            None
                        ),
                        "title": getattr(
                            workflow,
                            "title",
                            None
                        ),
                        "status": getattr(
                            workflow,
                            "status",
                            None
                        ),
                        "priority": getattr(
                            workflow,
                            "priority",
                            None
                        ),
                        "assignee": getattr(
                            workflow,
                            "assignee",
                            None
                        ),
                        "due_date": getattr(
                            workflow,
                            "due_date",
                            None
                        ),
                        "days_waiting": getattr(
                            workflow,
                            "days_waiting",
                            0
                        )
                    })

                state[
                    "jira_evidence"
                ] = jira_evidence

                logger.info(
                    "JIRA EVIDENCE RETRIEVED | count=%s",
                    len(jira_evidence)
                )

                observe_tool_result(
                    state,
                    "retrieve_jira_evidence",
                    len(jira_evidence),
                    len(jira_evidence) > 0
                )

            # =========================================
            # RETRIEVE SLACK EVIDENCE
            # =========================================

            elif step == "retrieve_slack_evidence":

                logger.info(
                    "EXECUTING | retrieve_slack_evidence"
                )

                slack_service = (
                    SlackService()
                )

                slack_evidence = []

                delayed_workflows = state.get(
                    "delayed_workflows",
                    state.get(
                        "workflows",
                        []
                    )
                )

                for workflow in delayed_workflows:

                    ticket_id = getattr(
                        workflow,
                        "ticket_id",
                        None
                    )

                    if not ticket_id:
                        continue

                    try:

                        evidence = (
                            slack_service
                            .get_ticket_evidence(
                                ticket_id
                            )
                        )

                        if evidence:

                            slack_evidence.extend(
                                evidence
                            )

                    except Exception as e:

                        logger.error(
                            "SLACK EVIDENCE ERROR | "
                            "ticket=%s | error=%s",
                            ticket_id,
                            e
                        )

                state[
                    "slack_evidence"
                ] = slack_evidence

                logger.info(
                    "SLACK EVIDENCE RETRIEVED | count=%s",
                    len(slack_evidence)
                )

                observe_tool_result(
                    state,
                    "retrieve_slack_evidence",
                    len(slack_evidence),
                    len(slack_evidence) > 0
                )

            # =========================================
            # COMPARE / COMBINE EVIDENCE
            # =========================================

            elif step == "compare_evidence":

                logger.info(
                    "EXECUTING | compare_evidence"
                )

                jira_evidence = state.get(
                    "jira_evidence",
                    []
                )

                slack_evidence = state.get(
                    "slack_evidence",
                    []
                )

                combined_evidence = {
                    "jira": jira_evidence,
                    "slack": slack_evidence
                }

                state[
                    "combined_evidence"
                ] = combined_evidence

                logger.info(
                    "EVIDENCE COMBINED | "
                    "jira=%s | slack=%s",
                    len(jira_evidence),
                    len(slack_evidence)
                )

                observe_tool_result(
                    state,
                    "compare_evidence",
                    (
                        len(jira_evidence)
                        + len(slack_evidence)
                    ),
                    (
                        len(jira_evidence) > 0
                        or len(slack_evidence) > 0
                    ),
                    details={
                        "jira_count": len(
                            jira_evidence
                        ),
                        "slack_count": len(
                            slack_evidence
                        )
                    }
                )

            # =========================================
            # OBSERVATION AGENT
            # =========================================

            elif step == "observe":

                logger.info(
                    "EXECUTING | observe"
                )

                observation_result = (
                    observation_agent(
                        state
                    )
                )

                state.update(
                    observation_result
                )

                observation = state.get(
                    "observation",
                    {}
                )

                logger.info(
                    "OBSERVATION COMPLETE | "
                    "status=%s | "
                    "sufficient=%s",
                    observation.get(
                        "status"
                    ),
                    observation.get(
                        "sufficient"
                    )
                )

                observe_tool_result(
                    state,
                    "observation_agent",
                    1,
                    bool(
                        observation.get(
                            "sufficient",
                            False
                        )
                    ),
                    details=observation
                )

            # =========================================
            # ANALYZE DELAY
            # =========================================

            elif step == "analyze_delay":

                logger.info(
                    "EXECUTING | analyze_delay"
                )

                result = pattern_agent(
                    state
                )

                state.update(
                    result
                )

                observe_tool_result(
                    state,
                    "analyze_delay",
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ),
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ) > 0
                )

            # =========================================
            # ANALYZE WORKFLOW
            # =========================================

            elif step == "analyze_workflow":

                logger.info(
                    "EXECUTING | analyze_workflow"
                )

                result = pattern_agent(
                    state
                )

                state.update(
                    result
                )

                observe_tool_result(
                    state,
                    "analyze_workflow",
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ),
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ) > 0
                )

            # =========================================
            # DETECT PATTERNS
            # =========================================

            elif step == "detect_patterns":

                logger.info(
                    "EXECUTING | detect_patterns"
                )

                result = pattern_agent(
                    state
                )

                state.update(
                    result
                )

                observe_tool_result(
                    state,
                    "detect_patterns",
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ),
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ) > 0
                )

            # =========================================
            # DETECT DELAYS
            # =========================================

            elif step == "detect_delays":

                logger.info(
                    "EXECUTING | detect_delays"
                )

                result = pattern_agent(
                    state
                )

                state.update(
                    result
                )

                observe_tool_result(
                    state,
                    "detect_delays",
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ),
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ) > 0
                )

            # =========================================
            # IDENTIFY ROOT CAUSE
            # =========================================

            elif step in (
                "identify_root_cause",
                "identify_root_causes"
            ):

                logger.info(
                    "EXECUTING | identify_root_cause"
                )

                if not state.get(
                    "insights"
                ):

                    logger.warning(
                        "ROOT CAUSE SKIPPED | "
                        "No insights available"
                    )

                    state[
                        "execution_status"
                    ] = "insufficient_evidence"

                    observe_tool_result(
                        state,
                        "identify_root_cause",
                        0,
                        False
                    )

                    break

                result = reasoning_agent(
                    state
                )

                state.update(
                    result
                )

                observe_tool_result(
                    state,
                    "reasoning_agent",
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ),
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ) > 0
                )

            # =========================================
            # GENERATE RECOMMENDATION
            # =========================================

            elif step in (
                "generate_recommendation",
                "generate_recommendations"
            ):

                logger.info(
                    "EXECUTING | generate_recommendation"
                )

                if not state.get(
                    "insights"
                ):

                    logger.warning(
                        "RECOMMENDATION SKIPPED | "
                        "No insights available"
                    )

                    state[
                        "execution_status"
                    ] = "insufficient_evidence"

                    observe_tool_result(
                        state,
                        "recommendation_agent",
                        0,
                        False
                    )

                    break

                result = recommendation_agent(
                    state
                )

                state.update(
                    result
                )

                observe_tool_result(
                    state,
                    "recommendation_agent",
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ),
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ) > 0
                )

            # =========================================
            # IDENTIFY BOTTLENECKS
            # =========================================

            elif step == "identify_bottlenecks":

                logger.info(
                    "EXECUTING | identify_bottlenecks"
                )

                if not state.get(
                    "insights"
                ):

                    logger.warning(
                        "BOTTLENECK ANALYSIS | "
                        "No insights available"
                    )

                    state[
                        "execution_status"
                    ] = "insufficient_evidence"

                    observe_tool_result(
                        state,
                        "identify_bottlenecks",
                        0,
                        False
                    )

                    break

                observe_tool_result(
                    state,
                    "identify_bottlenecks",
                    len(
                        state.get(
                            "insights",
                            []
                        )
                    ),
                    True
                )

            # =========================================
            # IDENTIFY PROBLEM
            # =========================================

            elif step == "identify_problem":

                logger.info(
                    "EXECUTING | identify_problem"
                )

                result = pattern_agent(
                    state
                )

                state.update(
                    result
                )

                observe_tool_result(
                    state,
                    "identify_problem",
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ),
                    len(
                        result.get(
                            "insights",
                            []
                        )
                    ) > 0
                )

            # =========================================
            # EXTRACT ISSUE KEY
            # =========================================

            elif step == "extract_issue_key":

                logger.info(
                    "EXECUTING | extract_issue_key"
                )

                issue_key = state.get(
                    "issue_key"
                )

                if not issue_key:

                    user_goal = state.get(
                        "user_goal",
                        ""
                    )

                    state[
                        "issue_key"
                    ] = user_goal

                observe_tool_result(
                    state,
                    "extract_issue_key",
                    1 if state.get(
                        "issue_key"
                    ) else 0,
                    bool(
                        state.get(
                            "issue_key"
                        )
                    )
                )

            # =========================================
            # RETRIEVE JIRA ISSUE
            # =========================================

            elif step == "retrieve_jira_issue":

                logger.info(
                    "EXECUTING | retrieve_jira_issue"
                )

                state[
                    "execution_status"
                ] = "jira_issue_retrieval_pending"

                observe_tool_result(
                    state,
                    "retrieve_jira_issue",
                    0,
                    False,
                    details={
                        "status": "pending"
                    }
                )

            # =========================================
            # RETURN ISSUE
            # =========================================

            elif step == "return_issue":

                logger.info(
                    "EXECUTING | return_issue"
                )

                state[
                    "execution_status"
                ] = "completed"

                observe_tool_result(
                    state,
                    "return_issue",
                    1,
                    True
                )

            # =========================================
            # UNDERSTAND GOAL
            # =========================================

            elif step == "understand_goal":

                logger.info(
                    "EXECUTING | understand_goal"
                )

                user_goal = state.get(
                    "user_goal"
                )

                if not user_goal:

                    logger.warning(
                        "USER GOAL NOT AVAILABLE"
                    )

                    state[
                        "execution_status"
                    ] = "missing_user_goal"

                    observe_tool_result(
                        state,
                        "understand_goal",
                        0,
                        False
                    )

                    break

                observe_tool_result(
                    state,
                    "understand_goal",
                    1,
                    True
                )

            # =========================================
            # UNKNOWN STEP
            # =========================================

            else:

                logger.warning(
                    "UNKNOWN PLAN STEP | "
                    "step=%s",
                    step
                )

                state[
                    "execution_status"
                ] = "unknown_step"

                observe_tool_result(
                    state,
                    step,
                    0,
                    False
                )

                break

            # --------------------------------
            # Step completed
            # --------------------------------

            logger.info(
                "PLAN STEP COMPLETE | "
                "step=%s | index=%s",
                step,
                current_step
            )

            current_step += 1

            state[
                "current_step"
            ] = current_step

        except Exception as e:

            logger.exception(
                "PLAN STEP FAILED | "
                "step=%s | error=%s",
                step,
                e
            )

            state[
                "execution_status"
            ] = "step_failed"

            state[
                "execution_error"
            ] = str(e)

            observe_tool_result(
                state,
                step,
                0,
                False,
                details={
                    "error": str(e)
                }
            )

            break

    # --------------------------------
    # Final status
    # --------------------------------

    if current_step >= len(plan):

        state[
            "execution_status"
        ] = "completed"

    logger.info(
        "PLAN EXECUTOR END | "
        "current_step=%s | "
        "total_steps=%s | "
        "status=%s",
        current_step,
        len(plan),
        state.get(
            "execution_status"
        )
    )

    logger.info(
        "OBSERVATIONS RECORDED | count=%s",
        len(
            state.get(
                "observations",
                []
            )

        )
    )

    return state