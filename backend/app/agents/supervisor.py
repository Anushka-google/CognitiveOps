import logging

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


# =========================================================
# AGENTIC LOOP SAFETY
# =========================================================

MAX_ITERATIONS = 5
MAX_STEP_REPEATS = 2


# =========================================================
# SUPERVISOR
# =========================================================

def supervisor(state: AgentState):
    """
    Supervisor responsible for controlling agent orchestration.

    It decides whether the workflow should:
    - continue executing the plan
    - move to reasoning
    - stop execution

    Phase 3.12:
    The supervisor also enforces bounded agentic looping
    through iteration and repeated-step limits.

    The supervisor does not perform business operations.
    """

    logger.info(
        "SUPERVISOR START"
    )

    execution_status = state.get(
        "execution_status"
    )

    current_step = state.get(
        "current_step",
        0
    )

    plan = state.get(
        "plan"
    ) or []

    reasoning_completed = state.get(
        "reasoning_completed",
        False
    )

    goal_completed = state.get(
        "goal_completed",
        False
    )

    self_correction_attempts = state.get(
        "self_correction_attempts",
        0
    )

    iteration_count = state.get(
        "iteration_count",
        0
    )

    last_step = state.get(
        "last_step"
    )

    step_repeat_count = state.get(
        "step_repeat_count",
        0
    )

    # =====================================================
    # TERMINATION CONDITIONS
    # =====================================================

    if execution_status == "awaiting_human_approval":

        logger.info(
            "SUPERVISOR DECISION | stop | "
            "reason=awaiting_human_approval"
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                "awaiting_human_approval"
            )
        }

    if execution_status in (
        "failed",
        "terminated"
    ):

        logger.info(
            "SUPERVISOR DECISION | stop | "
            "reason=%s",
            execution_status
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                execution_status
            )
        }

    if execution_status == "completed":

        logger.info(
            "SUPERVISOR DECISION | stop | "
            "reason=execution_completed"
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                "execution_completed"
            )
        }

    if goal_completed:

        logger.info(
            "SUPERVISOR DECISION | stop | "
            "reason=goal_completed"
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                "goal_completed"
            )
        }

    # =====================================================
    # AGENTIC LOOP LIMIT
    # =====================================================

    if iteration_count >= MAX_ITERATIONS:

        logger.warning(
            "SUPERVISOR DECISION | stop | "
            "reason=max_iterations | "
            "iteration_count=%s | "
            "max_iterations=%s",
            iteration_count,
            MAX_ITERATIONS
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                "max_iterations_reached"
            )
        }

    # =====================================================
    # SELF-CORRECTION LIMIT
    # =====================================================

    if self_correction_attempts >= 1:

        logger.info(
            "SUPERVISOR DECISION | stop | "
            "reason=self_correction_limit"
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                "self_correction_limit"
            )
        }

    # =====================================================
    # REASONING COMPLETE
    # =====================================================

    if reasoning_completed:

        logger.info(
            "SUPERVISOR DECISION | stop | "
            "reason=reasoning_completed"
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                "reasoning_completed"
            )
        }

    # =====================================================
    # REPEATED STEP PROTECTION
    # =====================================================

    if (
        last_step is not None
        and last_step == "plan_executor"
        and step_repeat_count >= MAX_STEP_REPEATS
    ):

        logger.warning(
            "SUPERVISOR DECISION | stop | "
            "reason=repeated_step | "
            "step=%s | "
            "repeat_count=%s",
            last_step,
            step_repeat_count
        )

        return {
            "last_step": "supervisor",
            "termination_reason": (
                "repeated_step_limit"
            )
        }

    # =====================================================
    # NORMAL EXECUTION
    # =====================================================

    logger.info(
        "SUPERVISOR STATE | "
        "current_step=%s | "
        "plan_length=%s | "
        "iteration=%s",
        current_step,
        len(plan),
        iteration_count
    )

    return {
        "last_step": "supervisor",
        "iteration_count": (
            iteration_count + 1
        )
    }


# =========================================================
# SUPERVISOR ROUTER
# =========================================================

def supervisor_router(state: AgentState):
    """
    Determines the next LangGraph node.

    Phase 3.12:
    Routing is bounded by iteration and repeated-step
    safety conditions.

    After evidence collection and observation are complete,
    the workflow moves to the reasoning agent.
    """

    execution_status = state.get(
        "execution_status"
    )

    current_step = state.get(
        "current_step",
        0
    )

    plan = state.get(
        "plan"
    ) or []

    reasoning_completed = state.get(
        "reasoning_completed",
        False
    )

    goal_completed = state.get(
        "goal_completed",
        False
    )

    self_correction_attempts = state.get(
        "self_correction_attempts",
        0
    )

    iteration_count = state.get(
        "iteration_count",
        0
    )

    last_step = state.get(
        "last_step"
    )

    step_repeat_count = state.get(
        "step_repeat_count",
        0
    )

    # =====================================================
    # STOP CONDITIONS
    # =====================================================

    if execution_status in (
        "awaiting_human_approval",
        "failed",
        "terminated",
        "completed"
    ):

        return "stop"

    if goal_completed:

        return "stop"

    if iteration_count >= MAX_ITERATIONS:

        return "stop"

    if self_correction_attempts >= 1:

        return "stop"

    if reasoning_completed:

        return "stop"

    if (
        last_step is not None
        and last_step == "plan_executor"
        and step_repeat_count >= MAX_STEP_REPEATS
    ):

        return "stop"

    # =====================================================
    # MOVE TO REASONING
    # =====================================================

    observation = state.get(
        "observation"
    )

    if (
        isinstance(
            observation,
            dict
        )
        and observation.get(
            "sufficient",
            False
        )
        and current_step >= 7
    ):

        return "reasoning"

    # =====================================================
    # PLAN COMPLETED
    # =====================================================

    if plan and current_step >= len(plan):

        return "reasoning"

    # =====================================================
    # CONTINUE PLAN
    # =====================================================

    return "continue"