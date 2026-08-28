import logging


logger = logging.getLogger(__name__)


def observation_agent(state):
    """
    Observes the results produced by previous
    tool/action execution.

    Observation decides whether the collected
    evidence is sufficient for the next reasoning step.

    It does not:
    - execute tools
    - call external APIs
    - call Gemini
    - generate recommendations

    It only observes the current state.
    """

    logger.info(
        "AGENT START | observation_agent"
    )

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
    # 5. Determine sufficiency
    # ==========================================

    sufficient = bool(
        jira_count > 0
        or slack_count > 0
    )

    # ==========================================
    # 6. Identify missing sources
    # ==========================================

    missing = []

    if jira_count == 0:

        missing.append(
            "jira"
        )

    if slack_count == 0:

        missing.append(
            "slack"
        )

    # ==========================================
    # 7. Build observation result
    # ==========================================

    if sufficient:

        status = "sufficient"

        reason = (
            "Operational evidence is available "
            "for reasoning."
        )

    else:

        status = "insufficient"

        reason = (
            "No operational evidence was found "
            "from Jira or Slack."
        )

    observation = {

        "status": status,

        "sufficient": sufficient,

        "reason": reason,

        "sources": sources,

        "missing": missing,

        "jira_count": jira_count,

        "slack_count": slack_count
    }

    # ==========================================
    # 8. Log observation
    # ==========================================

    logger.info(
        "OBSERVATION RESULT | "
        "status=%s | "
        "sufficient=%s | "
        "sources=%s | "
        "missing=%s",
        status,
        sufficient,
        sources,
        missing
    )

    logger.info(
        "AGENT END | observation_agent"
    )

    # ==========================================
    # 9. Return state update
    # ==========================================

    return {
        "observation": observation,
        "observation_status": status
    }