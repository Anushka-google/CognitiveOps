import logging
import time


logger = logging.getLogger(__name__)


def observation_agent(state):
    """
    Observes evidence produced by previous
    tool/action execution.

    Determines whether the evidence contains
    the information required for reliable reasoning.

    It does not:
    - execute tools
    - call external APIs
    - call Gemini
    - generate recommendations
    """

    logger.info(
        "AGENT START | observation_agent"
    )

    start_time = time.perf_counter()

    try:

        # ==========================================
        # 1. Read evidence from state
        # ==========================================

        jira_evidence = state.get(
            "jira_evidence",
            []
        )

        slack_evidence = state.get(
            "slack_evidence",
            []
        )

        combined_evidence = state.get(
            "combined_evidence",
            {}
        )

        # ==========================================
        # 2. Fallback to combined evidence
        # ==========================================

        if not jira_evidence:

            jira_evidence = combined_evidence.get(
                "jira",
                []
            )

        if not slack_evidence:

            slack_evidence = combined_evidence.get(
                "slack",
                []
            )

        # ==========================================
        # 3. Count observed evidence
        # ==========================================

        jira_count = len(
            jira_evidence
        )

        slack_count = len(
            slack_evidence
        )

        logger.info(
            "OBSERVATION INPUT | "
            "jira=%s | slack=%s",
            jira_count,
            slack_count
        )

        # ==========================================
        # 4. Identify available sources
        # ==========================================

        sources = []

        if jira_count > 0:

            sources.append(
                "jira"
            )

        if slack_count > 0:

            sources.append(
                "slack"
            )

        # ==========================================
        # 5. Evidence Quality Check
        # ==========================================

        jira_ticket = (
            jira_count > 0
        )

        jira_status = any(
            isinstance(item, dict)
            and (
                item.get("status")
                or item.get("issue_status")
                or item.get("state")
            )
            for item in jira_evidence
        )

        jira_timeline = any(
            isinstance(item, dict)
            and (
                item.get("timestamp")
                or item.get("created")
                or item.get("updated")
                or item.get("timeline")
                or item.get("days_waiting")
            )
            for item in jira_evidence
        )

        slack_message = (
            slack_count > 0
        )

        # ==========================================
        # 6. Identify Missing Information
        # ==========================================

        missing_information = []

        if not jira_ticket:

            missing_information.append(
                "affected ticket"
            )

        if not jira_status:

            missing_information.append(
                "ticket status"
            )

        if not jira_timeline:

            missing_information.append(
                "timeline"
            )

        if not slack_message:

            logger.info(
                "OBSERVATION | "
                "Slack evidence unavailable"
            )

        # ==========================================
        # 7. Determine Sufficiency
        # ==========================================

        sufficient = (
            jira_ticket
            and jira_status
            and jira_timeline
        )

        needs_correction = (
            not sufficient
        )

        if sufficient:

            status = "sufficient"

            reason = (
                "Required operational evidence "
                "is available for reasoning."
            )

        else:

            status = "insufficient"

            reason = (
                "Required evidence is missing "
                "for reliable reasoning."
            )

        # ==========================================
        # 8. Build Observation Result
        # ==========================================

        observation = {

            "status": status,

            "sufficient": sufficient,

            "needs_correction": (
                needs_correction
            ),

            "reason": reason,

            "sources": sources,

            "missing_information": (
                missing_information
            ),

            "jira_count": jira_count,

            "slack_count": slack_count,

            "evidence_quality": {

                "jira_ticket": jira_ticket,

                "jira_status": jira_status,

                "jira_timeline": jira_timeline,

                "slack_message": slack_message
            }
        }

        # ==========================================
        # 9. Logging
        # ==========================================

        logger.info(
            "OBSERVATION RESULT | "
            "status=%s | "
            "sufficient=%s | "
            "needs_correction=%s",
            status,
            sufficient,
            needs_correction
        )

        logger.info(
            "EVIDENCE QUALITY | "
            "jira_ticket=%s | "
            "jira_status=%s | "
            "jira_timeline=%s | "
            "slack_message=%s",
            jira_ticket,
            jira_status,
            jira_timeline,
            slack_message
        )

        logger.info(
            "SELF-CORRECTION CHECK | "
            "needed=%s | "
            "missing=%s",
            needs_correction,
            missing_information
        )

        # ==========================================
        # Structured Agent Output
        # ==========================================

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

        agent_outputs[
            "observation_agent"
        ] = {

            "agent": "observation_agent",

            "status": "success",

            "output": {

                "status": status,

                "sufficient": sufficient,

                "needs_correction": (
                    needs_correction
                ),

                "missing_information": (
                    missing_information
                ),

                "jira_count": jira_count,

                "slack_count": slack_count
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        logger.info(
            "STRUCTURED OUTPUT | "
            "agent=observation_agent | "
            "status=success"
        )

        logger.info(
            "AGENT END | observation_agent"
        )

        # ==========================================
        # 10. Return State Update
        # ==========================================

        return {

            "observation": observation,

            "observation_status": status,

            "self_correction_required": (
                needs_correction
            ),

            "agent_outputs": agent_outputs
        }

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | observation_agent | "
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
            "observation_agent"
        ] = {

            "agent": "observation_agent",

            "status": "failed",

            "output": None,

            "execution_time": (
                execution_time
            ),

            "error": str(e)
        }

        return {

            "agent_outputs": agent_outputs,

            "errors": [
                str(e)
            ]
        }