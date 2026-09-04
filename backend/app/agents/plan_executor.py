import logging
import time

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


def _copy_agent_outputs(state: AgentState):
    return dict(
        state.get(
            "agent_outputs",
            {}
        )
    )


def _copy_errors(state: AgentState):
    return list(
        state.get(
            "errors",
            []
        )
    )


def _result_count(result):
    """
    Safely calculate result count for structured output.
    """

    if result is None:
        return 0

    if isinstance(result, (list, tuple, set)):
        return len(result)

    if isinstance(result, dict):

        # A Jira issue is a dict but represents one result.
        return 1

    return 1


def plan_executor(state: AgentState):
    """
    Executes exactly ONE step from the planner-generated plan.

    The executor decides HOW to execute the current step.

    Important HITL rule:

        Agent proposes action
              ↓
        Human approval required
              ↓
        Executor STOPS
              ↓
        Approval API performs mutation

    This executor NEVER directly mutates Jira.
    """

    logger.info(
        "AGENT START | plan_executor"
    )

    start_time = time.perf_counter()

    try:

        # =====================================================
        # READ PLAN
        # =====================================================

        plan = list(
            state.get(
                "plan",
                []
            )
        )

        current_step = int(
            state.get(
                "current_step",
                0
            )
        )

        workflows = list(
            state.get(
                "workflows",
                []
            )
        )

        # =====================================================
        # NO PLAN
        # =====================================================

        if not plan:

            logger.warning(
                "PLAN EXECUTOR | no plan available"
            )

            return {

                "execution_status":
                    "failed",

                "execution_error":
                    "Planner returned an empty plan."
            }

        # =====================================================
        # PLAN FINISHED
        # =====================================================

        if current_step >= len(plan):

            logger.info(
                "PLAN EXECUTOR | plan already completed"
            )

            return {

                "current_step":
                    current_step,

                "execution_status":
                    "ready_for_reasoning"
            }

        # =====================================================
        # CURRENT STEP
        # =====================================================

        step = plan[current_step]

        logger.info(
            "PLAN EXECUTOR | "
            "current_step=%s | "
            "total_steps=%s | "
            "step=%s",
            current_step,
            len(plan),
            step
        )

        result = None

        sufficient = False

        # =====================================================
        # FIND WORKFLOW
        # =====================================================

        if step == "find_workflow":

            result = workflows

            sufficient = (
                len(workflows) > 0
            )

            logger.info(
                "EXECUTED find_workflow | "
                "result_count=%s",
                len(workflows)
            )

        # =====================================================
        # DETECT PATTERNS
        # =====================================================

        elif step == "detect_patterns":

            from app.services.workflow_analyzer import (
                WorkflowAnalyzer
            )

            analyzer = WorkflowAnalyzer()

            insights = (
                analyzer.analyze_workflow(
                    workflows
                )
            )

            result = insights

            sufficient = (
                len(insights) > 0
            )

            logger.info(
                "EXECUTED detect_patterns | "
                "insights=%s",
                len(insights)
            )

        # =====================================================
        # FIND DELAYED TASKS
        # =====================================================

        elif step == "find_delayed_tasks":

            delayed = []

            for workflow in workflows:

                days_waiting = getattr(
                    workflow,
                    "days_waiting",
                    0
                )

                try:
                    days_waiting = float(
                        days_waiting or 0
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    days_waiting = 0

                if days_waiting > 3:

                    delayed.append(
                        workflow
                    )

            result = delayed

            sufficient = (
                len(delayed) > 0
            )

            logger.info(
                "EXECUTED find_delayed_tasks | "
                "count=%s",
                len(delayed)
            )

        # =====================================================
        # RETRIEVE JIRA EVIDENCE
        # =====================================================

        elif step == "retrieve_jira_evidence":

            jira_evidence = []

            try:

                # -------------------------------------------------
                # First use existing evidence if available.
                # -------------------------------------------------

                existing_jira = state.get(
                    "jira_evidence"
                )

                if existing_jira:

                    jira_evidence = existing_jira

                # -------------------------------------------------
                # Otherwise retrieve from Jira.
                # -------------------------------------------------

                if not jira_evidence:

                    from app.services.jira_service import (
                        JiraService
                    )

                    jira_service = JiraService()

                    issue_key = state.get(
                        "issue_key"
                    )

                    if issue_key:

                        if hasattr(
                            jira_service,
                            "get_issue"
                        ):

                            jira_evidence = (
                                jira_service.get_issue(
                                    issue_key
                                )
                            )

                        elif hasattr(
                            jira_service,
                            "get_issue_details"
                        ):

                            jira_evidence = (
                                jira_service
                                .get_issue_details(
                                    issue_key
                                )
                            )

                    # -------------------------------------------------
                    # Fallback to all workflow records.
                    # -------------------------------------------------

                    if not jira_evidence:

                        jira_evidence = (
                            jira_service
                            .get_workflow_records()
                        )

            except Exception as e:

                logger.exception(
                    "JIRA EVIDENCE ERROR"
                )

                errors = _copy_errors(
                    state
                )

                errors.append({

                    "agent":
                        "plan_executor",

                    "step":
                        "retrieve_jira_evidence",

                    "error":
                        str(e)
                })

                return {

                    "errors":
                        errors,

                    "execution_status":
                        "failed",

                    "execution_error":
                        str(e)
                }

            result = jira_evidence

            # Jira may return either:
            #   list
            # or
            #   single dict.
            sufficient = bool(
                jira_evidence
            )

            logger.info(
                "EXECUTED retrieve_jira_evidence | "
                "available=%s",
                bool(jira_evidence)
            )

        # =====================================================
        # RETRIEVE SLACK EVIDENCE
        # =====================================================

        elif step == "retrieve_slack_evidence":

            slack_evidence = []

            try:

                slack_evidence = state.get(
                    "slack_evidence",
                    []
                )

                if not slack_evidence:

                    try:

                        from app.services.slack_service import (
                            SlackService
                        )

                        slack_service = (
                            SlackService()
                        )

                        if hasattr(
                            slack_service,
                            "get_evidence"
                        ):

                            slack_evidence = (
                                slack_service
                                .get_evidence(
                                    state.get(
                                        "user_goal",
                                        ""
                                    )
                                )
                            )

                        elif hasattr(
                            slack_service,
                            "search_messages"
                        ):

                            slack_evidence = (
                                slack_service
                                .search_messages(
                                    state.get(
                                        "user_goal",
                                        ""
                                    )
                                )
                            )

                    except ImportError:

                        logger.warning(
                            "Slack service not available"
                        )

            except Exception as e:

                logger.exception(
                    "SLACK EVIDENCE ERROR"
                )

            result = slack_evidence or []

            sufficient = bool(
                result
            )

            logger.info(
                "EXECUTED retrieve_slack_evidence | "
                "count=%s",
                (
                    len(result)
                    if isinstance(
                        result,
                        (list, tuple, set, dict)
                    )
                    else 0
                )
            )

        # =====================================================
        # COMPARE EVIDENCE
        # =====================================================

        elif step == "compare_evidence":

            jira_evidence = state.get(
                "jira_evidence",
                []
            )

            slack_evidence = state.get(
                "slack_evidence",
                []
            )

            combined_evidence = {

                "jira":
                    jira_evidence,

                "slack":
                    slack_evidence
            }

            result = combined_evidence

            sufficient = bool(
                jira_evidence
                or
                slack_evidence
            )

            logger.info(
                "EXECUTED compare_evidence | "
                "jira_available=%s | "
                "slack_available=%s",
                bool(jira_evidence),
                bool(slack_evidence)
            )

        # =====================================================
        # OBSERVE
        # =====================================================

        elif step == "observe":

            result = state.get(
                "observation",
                {}
            )

            sufficient = (
                result.get(
                    "sufficient",
                    False
                )
                if isinstance(
                    result,
                    dict
                )
                else False
            )

            logger.info(
                "EXECUTED observe"
            )

        # =====================================================
        # ROOT CAUSE
        # =====================================================

        elif step in (
            "identify_root_cause",
            "identify_root_causes"
        ):

            result = {

                "status":
                    "ready_for_reasoning",

                "message":
                    "Evidence prepared for root cause reasoning."
            }

            sufficient = True

            logger.info(
                "EXECUTED root cause preparation"
            )

        # =====================================================
        # BOTTLENECK
        # =====================================================

        elif step == "identify_bottlenecks":

            delayed = list(
                state.get(
                    "delayed_workflows",
                    []
                )
            )

            result = {

                "delayed_workflows":
                    delayed,

                "count":
                    len(delayed)
            }

            sufficient = (
                len(delayed) > 0
            )

        # =====================================================
        # PROBLEM IDENTIFICATION
        # =====================================================

        elif step == "identify_problem":

            insights = list(
                state.get(
                    "insights",
                    []
                )
            )

            result = insights

            sufficient = (
                len(insights) > 0
            )

        # =====================================================
        # GENERATE RECOMMENDATION
        # =====================================================

        elif step in (
            "generate_recommendation",
            "generate_recommendations"
        ):

            result = {

                "status":
                    "ready_for_recommendation",

                "message":
                    (
                        "Evidence and reasoning are ready "
                        "for recommendation generation."
                    )
            }

            sufficient = True

        # =====================================================
        # PROPOSE JIRA CHANGE
        #
        # CRITICAL HITL STEP
        # =====================================================

        elif step == "propose_jira_change":

            # -------------------------------------------------
            # Get issue key from state.
            # -------------------------------------------------

            issue_key = state.get(
                "issue_key"
            )

            # -------------------------------------------------
            # Safety fallback:
            # try extracting ticket_id from Jira evidence.
            # -------------------------------------------------

            if not issue_key:

                jira_evidence = state.get(
                    "jira_evidence",
                    []
                )

                if isinstance(
                    jira_evidence,
                    dict
                ):

                    issue_key = (
                        jira_evidence.get(
                            "ticket_id"
                        )
                        or
                        jira_evidence.get(
                            "key"
                        )
                    )

                elif isinstance(
                    jira_evidence,
                    list
                ):

                    for item in jira_evidence:

                        if not isinstance(
                            item,
                            dict
                        ):
                            continue

                        candidate = (
                            item.get(
                                "ticket_id"
                            )
                            or
                            item.get(
                                "key"
                            )
                        )

                        if candidate:

                            issue_key = candidate

                            break

            # -------------------------------------------------
            # Cannot safely propose an action without target.
            # -------------------------------------------------

            if not issue_key:

                logger.error(
                    "JIRA PROPOSAL FAILED | "
                    "No issue key available"
                )

                errors = _copy_errors(
                    state
                )

                errors.append({

                    "agent":
                        "plan_executor",

                    "step":
                        "propose_jira_change",

                    "error":
                        "No Jira issue key available."
                })

                return {

                    "errors":
                        errors,

                    "execution_status":
                        "failed",

                    "execution_error":
                        "No Jira issue key available."
                }

            # -------------------------------------------------
            # Create concrete proposed action.
            #
            # IMPORTANT:
            # This DOES NOT call Jira.
            # -------------------------------------------------

            proposed_action = {

                "action_type":
                    "jira_update_priority",

                "target":
                    issue_key,

                "field":
                    "priority",

                "new_value":
                    "Highest",

                "description":
                    (
                        f"Update Jira issue "
                        f"{issue_key} priority to Highest."
                    ),

                "impact_level":
                    "high",

                "requires_human_approval":
                    True
            }

            result = proposed_action

            sufficient = True

            # -------------------------------------------------
            # CRITICAL:
            # Return immediately with HITL state.
            #
            # Do NOT increment current_step and continue
            # into observation/self-correction.
            # -------------------------------------------------

            execution_time = (
                time.perf_counter()
                - start_time
            )

            agent_outputs = (
                _copy_agent_outputs(
                    state
                )
            )

            agent_outputs[
                "plan_executor"
            ] = {

                "agent":
                    "plan_executor",

                "status":
                    "awaiting_approval",

                "output": {

                    "step":
                        step,

                    "step_index":
                        current_step,

                    "next_step":
                        current_step,

                    "total_steps":
                        len(plan),

                    "result_count":
                        1,

                    "sufficient":
                        True,

                    "issue_key":
                        issue_key,

                    "proposed_action":
                        proposed_action,

                    "approval_required":
                        True,

                    "approval_status":
                        "pending"
                },

                "execution_time":
                    execution_time,

                "error":
                    None
            }

            logger.warning(
                "HITL PAUSE | "
                "Jira action proposed | "
                "issue=%s | "
                "approval=pending",
                issue_key
            )

            logger.info(
                "AGENT END | plan_executor | "
                "awaiting human approval"
            )

            return {

                "issue_key":
                    issue_key,

                "proposed_action":
                    proposed_action,

                "approval_required":
                    True,

                "approval_status":
                    "pending",

                "approval_reason":
                    (
                        "Jira priority mutation "
                        "requires human approval."
                    ),

                "execution_status":
                    "awaiting_human_approval",

                "execution_error":
                    None,

                "agent_outputs":
                    agent_outputs,

                "goal_completed":
                    False,

                "termination_reason":
                    "human_approval_required"
            }

        # =====================================================
        # EXTRACT ISSUE KEY
        # =====================================================

        elif step == "extract_issue_key":

            issue_key = state.get(
                "issue_key"
            )

            result = issue_key

            sufficient = bool(
                issue_key
            )

        # =====================================================
        # RETRIEVE JIRA ISSUE
        # =====================================================

        elif step == "retrieve_jira_issue":

            issue_key = state.get(
                "issue_key"
            )

            if not issue_key:

                raise ValueError(
                    "issue_key is required"
                )

            from app.services.jira_service import (
                JiraService
            )

            jira_service = JiraService()

            if hasattr(
                jira_service,
                "get_issue"
            ):

                result = (
                    jira_service.get_issue(
                        issue_key
                    )
                )

            elif hasattr(
                jira_service,
                "get_issue_details"
            ):

                result = (
                    jira_service
                    .get_issue_details(
                        issue_key
                    )
                )

            else:

                result = None

            sufficient = bool(
                result
            )

        # =====================================================
        # RETURN ISSUE
        # =====================================================

        elif step == "return_issue":

            result = state.get(
                "jira_evidence",
                []
            )

            sufficient = bool(
                result
            )

        # =====================================================
        # UNDERSTAND GOAL
        # =====================================================

        elif step == "understand_goal":

            result = {

                "user_goal":
                    state.get(
                        "user_goal"
                    ),

                "intent":
                    state.get(
                        "intent"
                    )
            }

            sufficient = True

        # =====================================================
        # UNKNOWN STEP
        # =====================================================

        else:

            raise ValueError(
                f"Unknown plan step: {step}"
            )

        # =====================================================
        # STATE UPDATES
        # =====================================================

        state_update = {}

        if step == "find_workflow":

            state_update[
                "workflows"
            ] = result

        elif step == "detect_patterns":

            state_update[
                "insights"
            ] = result

        elif step == "find_delayed_tasks":

            state_update[
                "delayed_workflows"
            ] = result

        elif step == "retrieve_jira_evidence":

            state_update[
                "jira_evidence"
            ] = result

            state_update[
                "evidence"
            ] = {

                **state.get(
                    "evidence",
                    {}
                ),

                "jira":
                    result
            }

        elif step == "retrieve_slack_evidence":

            state_update[
                "slack_evidence"
            ] = result

            state_update[
                "evidence"
            ] = {

                **state.get(
                    "evidence",
                    {}
                ),

                "slack":
                    result
            }

        elif step == "compare_evidence":

            state_update[
                "combined_evidence"
            ] = result

            state_update[
                "evidence"
            ] = result

        # =====================================================
        # NORMAL STEP PROGRESSION
        # =====================================================

        next_step = (
            current_step + 1
        )

        state_update[
            "current_step"
        ] = next_step

        # =====================================================
        # EXECUTION STATUS
        # =====================================================

        if next_step >= len(plan):

            execution_status = (
                "ready_for_reasoning"
            )

        else:

            execution_status = (
                "running"
            )

        state_update[
            "execution_status"
        ] = execution_status

        # =====================================================
        # STRUCTURED OUTPUT
        # =====================================================

        execution_time = (
            time.perf_counter()
            - start_time
        )

        agent_outputs = (
            _copy_agent_outputs(
                state
            )
        )

        agent_outputs[
            "plan_executor"
        ] = {

            "agent":
                "plan_executor",

            "status":
                "success",

            "output": {

                "step":
                    step,

                "step_index":
                    current_step,

                "next_step":
                    next_step,

                "total_steps":
                    len(plan),

                "result_count":
                    _result_count(result),

                "sufficient":
                    sufficient
            },

            "execution_time":
                execution_time,

            "error":
                None
        }

        state_update[
            "agent_outputs"
        ] = agent_outputs

        logger.info(
            "PLAN STEP COMPLETE | "
            "step=%s | "
            "current=%s | "
            "next=%s | "
            "status=%s",
            step,
            current_step,
            next_step,
            execution_status
        )

        logger.info(
            "AGENT END | plan_executor"
        )

        return state_update

    # =========================================================
    # ERROR
    # =========================================================

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | plan_executor | "
            "execution_time=%.2fs",
            execution_time
        )

        agent_outputs = (
            _copy_agent_outputs(
                state
            )
        )

        agent_outputs[
            "plan_executor"
        ] = {

            "agent":
                "plan_executor",

            "status":
                "failed",

            "output":
                None,

            "execution_time":
                execution_time,

            "error":
                str(e)
        }

        errors = _copy_errors(
            state
        )

        errors.append({

            "agent":
                "plan_executor",

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