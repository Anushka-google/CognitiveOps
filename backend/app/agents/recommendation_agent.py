import logging
import time

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


def recommendation_agent(
    state: AgentState
):
    """
    Processes generated workflow insights
    and returns structured recommendation output.

    Responsibilities:
    - Process generated insights
    - Identify high-priority recommendations
    - Mark high-priority recommendations
    - Preserve existing agent outputs
    - Return predictable state structure

    Does NOT:
    - call external APIs
    - call Gemini
    - retrieve evidence
    - modify Jira
    - modify workflow source data
    """

    logger.info(
        "AGENT START | recommendation_agent"
    )

    start_time = time.perf_counter()

    try:

        # =====================================================
        # 1. READ EXISTING INSIGHTS
        # =====================================================

        insights = state.get(
            "insights",
            []
        )

        if not isinstance(
            insights,
            list
        ):

            logger.warning(
                "INVALID INSIGHTS TYPE | "
                "expected=list | actual=%s",
                type(insights).__name__
            )

            insights = []

        logger.info(
            "RECOMMENDATION INPUT | "
            "insights=%s",
            len(insights)
        )

        high_priority_count = 0

        processed_count = 0

        skipped_count = 0

        # =====================================================
        # 2. PROCESS EACH INSIGHT
        # =====================================================

        for insight in insights:

            # -------------------------------------------------
            # Safety check
            # -------------------------------------------------

            if insight is None:

                skipped_count += 1

                logger.warning(
                    "SKIPPING NULL INSIGHT"
                )

                continue

            # -------------------------------------------------
            # Support object-style insights
            # -------------------------------------------------

            if hasattr(
                insight,
                "severity"
            ):

                severity = getattr(
                    insight,
                    "severity",
                    None
                )

                recommendation = getattr(
                    insight,
                    "recommendation",
                    None
                )

                is_object = True

            # -------------------------------------------------
            # Support dictionary-style insights
            # -------------------------------------------------

            elif isinstance(
                insight,
                dict
            ):

                severity = insight.get(
                    "severity"
                )

                recommendation = insight.get(
                    "recommendation"
                )

                is_object = False

            # -------------------------------------------------
            # Unknown structure
            # -------------------------------------------------

            else:

                skipped_count += 1

                logger.warning(
                    "SKIPPING INVALID INSIGHT | "
                    "type=%s",
                    type(insight).__name__
                )

                continue

            processed_count += 1

            # =================================================
            # 3. NORMALIZE SEVERITY
            # =================================================

            severity_text = str(
                severity or ""
            ).strip().lower()

            # =================================================
            # 4. PROCESS HIGH PRIORITY
            # =================================================

            if (
                severity_text == "high"
                and recommendation
            ):

                recommendation_text = str(
                    recommendation
                ).strip()

                # ---------------------------------------------
                # Avoid duplicate prefix
                # ---------------------------------------------

                if not recommendation_text.startswith(
                    "[HIGH PRIORITY]"
                ):

                    recommendation_text = (
                        "[HIGH PRIORITY] "
                        + recommendation_text
                    )

                    # -----------------------------------------
                    # Update original insight
                    # -----------------------------------------

                    if is_object:

                        setattr(
                            insight,
                            "recommendation",
                            recommendation_text
                        )

                    else:

                        insight[
                            "recommendation"
                        ] = recommendation_text

                high_priority_count += 1

                logger.info(
                    "HIGH PRIORITY RECOMMENDATION | "
                    "severity=%s",
                    severity
                )

        # =====================================================
        # 5. EXECUTION TIME
        # =====================================================

        execution_time = (
            time.perf_counter()
            - start_time
        )

        # =====================================================
        # 6. STRUCTURED AGENT OUTPUT
        # =====================================================

        recommendation_output = {

            "status": "success",

            "result_count": (
                len(insights)
            ),

            "processed_count": (
                processed_count
            ),

            "skipped_count": (
                skipped_count
            ),

            "high_priority_count": (
                high_priority_count
            ),

            "output": insights
        }

        # =====================================================
        # 7. PRESERVE PREVIOUS AGENT OUTPUTS
        # =====================================================

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        agent_outputs[
            "recommendation_agent"
        ] = {

            "agent": (
                "recommendation_agent"
            ),

            "status": "success",

            "output": {

                "result_count": (
                    len(insights)
                ),

                "processed_count": (
                    processed_count
                ),

                "skipped_count": (
                    skipped_count
                ),

                "high_priority_count": (
                    high_priority_count
                )
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        # =====================================================
        # 8. LOGGING
        # =====================================================

        logger.info(
            "AGENT END | recommendation_agent | "
            "execution_time=%.2fs | "
            "insights=%s | "
            "high_priority=%s",
            execution_time,
            len(insights),
            high_priority_count
        )

        logger.info(
            "RECOMMENDATION SUMMARY | "
            "processed=%s | "
            "skipped=%s | "
            "high_priority=%s",
            processed_count,
            skipped_count,
            high_priority_count
        )

        logger.info(
            "STRUCTURED OUTPUT | "
            "agent=recommendation_agent | "
            "status=success | "
            "result_count=%s",
            len(insights)
        )

        # =====================================================
        # 9. RETURN STATE UPDATE
        # =====================================================

        return {

            "insights": insights,

            "agent_outputs": agent_outputs
        }

    # =========================================================
    # 10. ERROR HANDLING
    # =========================================================

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | recommendation_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        # -----------------------------------------------------
        # Preserve existing agent outputs
        # -----------------------------------------------------

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        error_output = {

            "agent": (
                "recommendation_agent"
            ),

            "status": "failed",

            "output": {

                "result_count": 0,

                "high_priority_count": 0
            },

            "execution_time": (
                execution_time
            ),

            "error": str(e)
        }

        agent_outputs[
            "recommendation_agent"
        ] = error_output

        # -----------------------------------------------------
        # Preserve existing errors
        # -----------------------------------------------------

        errors = list(
            state.get(
                "errors",
                []
            )
        )

        errors.append({

            "agent": (
                "recommendation_agent"
            ),

            "error": str(e)
        })

        return {

            "agent_outputs": agent_outputs,

            "errors": errors
        }