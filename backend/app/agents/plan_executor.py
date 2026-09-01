import logging
import time

from app.agents.pattern_agent import (
    pattern_agent
)

from app.agents.reasoning_agent import (
    reasoning_agent
)

from app.agents.recommendation_agent import (
    recommendation_agent
)

from app.agents.state import (
    AgentState
)


logger = logging.getLogger(__name__)


# =====================================================
# Plan Executor
# =====================================================

def plan_executor(
    state: AgentState
):

    logger.info(
        "AGENT START | plan_executor"
    )

    start_time = time.perf_counter()

    try:

        # =================================================
        # Read plan state
        # =================================================

        plan = state.get(
            "plan",
            []
        )

        current_step = state.get(
            "current_step",
            0
        )

        iteration_count = state.get(
            "iteration_count",
            0
        )

        # =================================================
        # Iteration limit
        #
        # Allow complete plan to execute.
        # =================================================

        max_iterations = max(
            5,
            len(plan)
        )

        # =================================================
        # State Containers
        # =================================================

        tool_results = dict(
            state.get(
                "tool_results",
                {}
            )
        )

        evidence = dict(
            state.get(
                "evidence",
                {}
            )
        )

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        observations = list(
            state.get(
                "observations",
                []
            )
        )

        errors = list(
            state.get(
                "errors",
                []
            )
        )

        # =================================================
        # HITL State
        # =================================================

        proposed_action = dict(
            state.get(
                "proposed_action",
                {}
            )
        )

        approval_required = state.get(
            "approval_required",
            False
        )

        approval_status = state.get(
            "approval_status",
            None
        )

        approval_reason = state.get(
            "approval_reason",
            None
        )

        logger.info(
            "HUMAN-IN-THE-LOOP | "
            "required=%s | "
            "status=%s | "
            "action=%s",
            approval_required,
            approval_status,
            proposed_action.get(
                "action_type"
            )
        )

        # =================================================
        # Validate plan
        # =================================================

        if not plan:

            logger.warning(
                "PLAN EXECUTOR | "
                "NO PLAN AVAILABLE"
            )

            return {

                "execution_status": (
                    "terminated"
                ),

                "termination_reason": (
                    "empty_plan"
                ),

                "goal_completed": False
            }

        # =================================================
        # Iteration Safety
        # =================================================

        if iteration_count >= max_iterations:

            logger.warning(
                "TERMINATION | "
                "reason=max_iterations_reached | "
                "iteration=%s | "
                "max_iterations=%s",
                iteration_count,
                max_iterations
            )

            return {

                "current_step": (
                    current_step
                ),

                "execution_status": (
                    "terminated"
                ),

                "termination_reason": (
                    "max_iterations_reached"
                ),

                "goal_completed": False,

                "iteration_count": (
                    iteration_count
                ),

                "tool_results": (
                    tool_results
                ),

                "evidence": (
                    evidence
                ),

                "agent_outputs": (
                    agent_outputs
                ),

                "observations": (
                    observations
                ),

                "errors": (
                    errors
                )
            }

        iteration_count += 1

        logger.info(
            "ITERATION | current=%s | max=%s",
            iteration_count,
            max_iterations
        )

        # =================================================
        # Plan Completed
        # =================================================

        if current_step >= len(plan):

            logger.info(
                "PLAN EXECUTOR | "
                "ALL PLAN STEPS COMPLETED"
            )

            return {

                "current_step": (
                    current_step
                ),

                "execution_status": (
                    "completed"
                ),

                "goal_completed": True,

                "termination_reason": (
                    "plan_completed"
                ),

                "iteration_count": (
                    iteration_count
                ),

                "tool_results": (
                    tool_results
                ),

                "evidence": (
                    evidence
                ),

                "agent_outputs": (
                    agent_outputs
                ),

                "observations": (
                    observations
                ),

                "errors": (
                    errors
                ),

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
                )
            }

        # =================================================
        # Current Step
        # =================================================

        step = plan[current_step]

        logger.info(
            "PLAN STEP START | "
            "step=%s | index=%s",
            step,
            current_step
        )

        # =================================================
        # HIGH-IMPACT JIRA PROPOSAL
        #
        # HUMAN-IN-THE-LOOP boundary.
        #
        # IMPORTANT:
        # No Jira mutation happens here.
        # =================================================

        if step == "propose_jira_change":

            jira_evidence = state.get(
                "jira_evidence",
                []
            )

            issue_key = state.get(
                "issue_key"
            )

            # -------------------------------------------------
            # Try to obtain issue key from Jira evidence
            # -------------------------------------------------

            if not issue_key:

                for item in jira_evidence:

                    if isinstance(
                        item,
                        dict
                    ):

                        issue_key = item.get(
                            "ticket_id"
                        )

                        if not issue_key:

                            issue_key = item.get(
                                "issue_key"
                            )

                    else:

                        issue_key = getattr(
                            item,
                            "ticket_id",
                            None
                        )

                        if not issue_key:

                            issue_key = getattr(
                                item,
                                "issue_key",
                                None
                            )

                    if issue_key:

                        break

            # -------------------------------------------------
            # No issue → cannot propose action
            # -------------------------------------------------

            if not issue_key:

                logger.warning(
                    "HITL PROPOSAL FAILED | "
                    "No Jira issue key available"
                )

                errors.append(
                    {
                        "step": step,

                        "error": (
                            "No Jira issue key "
                            "available for approval."
                        )
                    }
                )

                return {

                    "current_step": (
                        current_step
                    ),

                    "execution_status": (
                        "failed"
                    ),

                    "execution_error": (
                        "No Jira issue key available."
                    ),

                    "termination_reason": (
                        "missing_issue_key"
                    ),

                    "goal_completed": False,

                    "iteration_count": (
                        iteration_count
                    ),

                    "errors": errors
                }

            # -------------------------------------------------
            # Store issue key
            # -------------------------------------------------

            proposed_action = {

                "action_type": (
                    "jira_update_priority"
                ),

                "target": issue_key,

                "field": "priority",

                "new_value": "Highest",

                "description": (
                    f"Update Jira issue "
                    f"{issue_key} priority to "
                    f"Highest."
                ),

                "impact_level": "high",

                "jira_evidence_count": (
                    len(jira_evidence)
                ),

                "requires_human_approval": True
            }

            approval_required = True

            approval_status = "pending"

            approval_reason = (
                "Changing Jira priority is an "
                "operational action and therefore "
                "requires human approval before "
                "the Jira API is called."
            )

            logger.warning(
                "HUMAN-IN-THE-LOOP | "
                "HIGH-IMPACT ACTION PROPOSED | "
                "action=jira_update_priority | "
                "issue=%s | "
                "new_priority=Highest",
                issue_key
            )

            agent_outputs[
                "plan_executor"
            ] = {

                "agent": (
                    "plan_executor"
                ),

                "status": (
                    "awaiting_approval"
                ),

                "output": {

                    "step": step,

                    "proposed_action": (
                        proposed_action
                    ),

                    "approval_required": True,

                    "approval_status": (
                        "pending"
                    )
                },

                "execution_time": (
                    time.perf_counter()
                    - start_time
                ),

                "error": None
            }

            observations.append(
                {
                    "step": step,

                    "status": (
                        "awaiting_approval"
                    ),

                    "result_count": 1,

                    "sufficient": False
                }
            )

            # =================================================
            # STOP HERE
            #
            # NO TOOL EXECUTION
            # =================================================

            return {

                "current_step": (
                    current_step
                ),

                "iteration_count": (
                    iteration_count
                ),

                "last_step": step,

                "step_repeat_count": (
                    state.get(
                        "step_repeat_count",
                        0
                    )
                ),

                "proposed_action": (
                    proposed_action
                ),

                "approval_required": True,

                "approval_status": (
                    approval_status
                ),

                "approval_reason": (
                    approval_reason
                ),

                "execution_status": (
                    "awaiting_human_approval"
                ),

                "termination_reason": (
                    "human_approval_required"
                ),

                "goal_completed": False,

                "tool_results": (
                    tool_results
                ),

                "evidence": (
                    evidence
                ),

                "agent_outputs": (
                    agent_outputs
                ),

                "observations": (
                    observations
                ),

                "errors": (
                    errors
                )
            }

        # =================================================
        # Execute normal steps
        # =================================================

        result = None

        sufficient = False

        # =================================================
        # FIND WORKFLOW
        # =================================================

        if step == "find_workflow":

            result = state.get(
                "workflows",
                []
            )

            tool_results[
                "find_workflow"
            ] = result

        # =================================================
        # FIND DELAYED TASKS
        # =================================================

        elif step == "find_delayed_tasks":

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

            result = delayed_workflows

            tool_results[
                "find_delayed_tasks"
            ] = result

            logger.info(
                "DELAYED WORKFLOWS FOUND | "
                "count=%s",
                len(
                    delayed_workflows
                )
            )

        # =================================================
        # RETRIEVE JIRA EVIDENCE
        # =================================================

        elif step == "retrieve_jira_evidence":

            # Jira workflow records were already retrieved
            # by WorkflowGraphService before the agent graph
            # started. Use them as the Jira evidence source.

            result = state.get(
                "jira_evidence"
            ) or state.get(
                "workflows",
                []
            )

            evidence[
                "jira"
            ] = result

            # -------------------------------------------------
            # Keep Jira evidence in state
            # -------------------------------------------------

            state[
                "jira_evidence"
            ] = result

            # -------------------------------------------------
            # Extract issue key when possible
            # -------------------------------------------------

            if not state.get(
                "issue_key"
            ):

                for item in result:

                    if isinstance(
                        item,
                        dict
                    ):

                        key = item.get(
                            "ticket_id"
                        )

                        if not key:

                            key = item.get(
                                "issue_key"
                            )

                        if not key:

                            key = item.get(
                                "key"
                            )

                    else:

                        key = getattr(
                            item,
                            "ticket_id",
                            None
                        )

                        if not key:

                            key = getattr(
                                item,
                                "issue_key",
                                None
                            )

                        if not key:

                            key = getattr(
                                item,
                                "key",
                                None
                            )

                    if key:

                        state[
                            "issue_key"
                        ] = key

                        logger.info(
                            "JIRA ISSUE KEY | "
                            "issue=%s",
                            key
                        )

                        break

            sufficient = (
                len(result) > 0
            )

        # =================================================
        # RETRIEVE SLACK EVIDENCE
        # =================================================

        elif step == "retrieve_slack_evidence":

            result = state.get(
                "slack_evidence",
                []
            )

            evidence[
                "slack"
            ] = result

            state[
                "slack_evidence"
            ] = result

            sufficient = (
                len(result) > 0
            )

        # =================================================
        # COMPARE EVIDENCE
        # =================================================

        elif step == "compare_evidence":

            jira = state.get(
                "jira_evidence",
                []
            )

            slack = state.get(
                "slack_evidence",
                []
            )

            combined = {

                "jira": jira,

                "slack": slack
            }

            result = (
                jira + slack
            )

            evidence[
                "combined"
            ] = combined

            state[
                "combined_evidence"
            ] = combined

            sufficient = (
                len(result) > 0
            )

            logger.info(
                "EVIDENCE COMBINED | "
                "jira=%s | slack=%s",
                len(jira),
                len(slack)
            )

        # =================================================
        # OBSERVE
        # =================================================

        elif step == "observe":

            observation = state.get(
                "observation",
                {}
            )

            result = observation

            sufficient = observation.get(
                "sufficient",
                False
            )

        # =================================================
        # PATTERN AGENT
        # =================================================

        elif step in (
            "detect_patterns",
            "detect_delays"
        ):

            result = pattern_agent(
                state
            )

            if result:

                state.update(
                    result
                )

        # =================================================
        # ROOT CAUSE
        # =================================================

        elif step in (
            "identify_root_cause",
            "identify_root_causes"
        ):

            if not state.get(
                "insights"
            ):

                logger.warning(
                    "ROOT CAUSE SKIPPED | "
                    "No insights available"
                )

                result = []

            else:

                result = reasoning_agent(
                    state
                )

                if result:

                    state.update(
                        result
                    )

        # =================================================
        # RECOMMENDATION
        # =================================================

        elif step in (
            "generate_recommendation",
            "generate_recommendations"
        ):

            if not state.get(
                "insights"
            ):

                logger.warning(
                    "RECOMMENDATION SKIPPED | "
                    "No insights available"
                )

                result = []

            else:

                result = recommendation_agent(
                    state
                )

                if result:

                    state.update(
                        result
                    )

        # =================================================
        # OTHER ANALYSIS STEPS
        # =================================================

        elif step in (
            "identify_bottlenecks",
            "identify_problem",
            "understand_goal"
        ):

            result = state.get(
                "insights",
                []
            )

        # =================================================
        # JIRA ISSUE
        # =================================================

        elif step == "extract_issue_key":

            result = state.get(
                "issue_key"
            )

            tool_results[
                "extract_issue_key"
            ] = result

            sufficient = (
                result is not None
            )

        elif step == "retrieve_jira_issue":

            result = state.get(
                "jira_evidence",
                []
            )

            evidence[
                "jira"
            ] = result

            sufficient = (
                len(result) > 0
            )

        elif step == "return_issue":

            result = state.get(
                "jira_evidence",
                []
            )

            sufficient = (
                len(result) > 0
            )

        # =================================================
        # UNKNOWN STEP
        # =================================================

        else:

            logger.warning(
                "UNKNOWN PLAN STEP | "
                "step=%s",
                step
            )

            result = None

        # =================================================
        # Store result
        # =================================================

        if step not in tool_results:

            tool_results[
                step
            ] = result

        # =================================================
        # Result count
        # =================================================

        if isinstance(
            result,
            (list, tuple, dict)
        ):

            result_count = len(
                result
            )

        elif result is None:

            result_count = 0

        else:

            result_count = 1

        # =================================================
        # Observation
        # =================================================

        observations.append(
            {

                "step": step,

                "result_count": (
                    result_count
                ),

                "sufficient": (
                    sufficient
                )
            }
        )

        logger.info(
            "OBSERVATION | "
            "tool=%s | "
            "result_count=%s | "
            "sufficient=%s",
            step,
            result_count,
            sufficient
        )

        # =================================================
        # Structured output
        # =================================================

        agent_outputs[
            "plan_executor"
        ] = {

            "agent": (
                "plan_executor"
            ),

            "status": "success",

            "output": {

                "step": step,

                "result_count": (
                    result_count
                ),

                "sufficient": (
                    sufficient
                )
            },

            "execution_time": (
                time.perf_counter()
                - start_time
            ),

            "error": None
        }

        # =================================================
        # Advance step
        # =================================================

        next_step = (
            current_step + 1
        )

        if next_step >= len(plan):

            execution_status = (
                "completed"
            )

            goal_completed = True

            termination_reason = (
                "plan_completed"
            )

        else:

            execution_status = (
                "running"
            )

            goal_completed = False

            termination_reason = None

        logger.info(
            "PLAN STEP COMPLETE | "
            "step=%s | index=%s",
            step,
            current_step
        )

        logger.info(
            "PLAN EXECUTOR END | "
            "current_step=%s | "
            "total_steps=%s | "
            "status=%s",
            next_step,
            len(plan),
            execution_status
        )

        logger.info(
            "OBSERVATIONS RECORDED | count=%s",
            len(observations)
        )

        logger.info(
            "SHORT-TERM MEMORY | "
            "tool_results=%s | "
            "evidence=%s | "
            "agent_outputs=%s",
            len(tool_results),
            len(evidence),
            len(agent_outputs)
        )

        logger.info(
            "HUMAN-IN-THE-LOOP | "
            "required=%s | "
            "status=%s",
            approval_required,
            approval_status
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AGENT END | plan_executor | "
            "execution_time=%.2fs",
            execution_time
        )

        return {

            "current_step": (
                next_step
            ),

            "iteration_count": (
                iteration_count
            ),

            "last_step": step,

            "step_repeat_count": (
                state.get(
                    "step_repeat_count",
                    0
                )
            ),

            "tool_results": (
                tool_results
            ),

            "evidence": (
                evidence
            ),

            "observations": (
                observations
            ),

            "agent_outputs": (
                agent_outputs
            ),

            "errors": (
                errors
            ),

            "execution_status": (
                execution_status
            ),

            "goal_completed": (
                goal_completed
            ),

            "termination_reason": (
                termination_reason
            ),

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
            )
        }

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | "
            "plan_executor | "
            "execution_time=%.2fs",
            execution_time
        )

        errors = list(
            state.get(
                "errors",
                []
            )
        )

        errors.append(
            {
                "step": (
                    state.get(
                        "current_step"
                    )
                ),

                "error": str(e)
            }
        )

        return {

            "agent_outputs": {

                **state.get(
                    "agent_outputs",
                    {}
                ),

                "plan_executor": {

                    "agent": (
                        "plan_executor"
                    ),

                    "status": (
                        "failed"
                    ),

                    "output": None,

                    "execution_time": (
                        execution_time
                    ),

                    "error": str(e)
                }
            },

            "errors": errors,

            "execution_status": (
                "failed"
            ),

            "execution_error": (
                str(e)
            ),

            "termination_reason": (
                "executor_error"
            ),

            "goal_completed": False
        }