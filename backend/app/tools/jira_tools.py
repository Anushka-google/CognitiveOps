import logging

from app.services.jira_service import (
    JiraService
)

from app.services.trace_service import (
    trace_log
)


logger = logging.getLogger(__name__)


# =========================================================
# TOOL POLICY
# =========================================================

ALLOWED_JIRA_TOOLS = {
    "update_jira_priority"
}


ALLOWED_PRIORITY_VALUES = {
    "Highest"
}


# =========================================================
# UPDATE JIRA PRIORITY
# =========================================================

def update_jira_priority(
    issue_key: str,
    priority_name: str = "Highest"
):
    """
    Controlled Jira tool for updating issue priority.

    This tool is intended to run only after
    the human approval gate has passed.
    """

    # =====================================================
    # ISSUE KEY VALIDATION
    # =====================================================

    if not isinstance(
        issue_key,
        str
    ):

        raise ValueError(
            "Jira issue key must be a string."
        )

    issue_key = (
        issue_key.strip()
    )

    if not issue_key:

        raise ValueError(
            "Jira issue key cannot be empty."
        )

    # =====================================================
    # PRIORITY VALIDATION
    # =====================================================

    if priority_name not in (
        ALLOWED_PRIORITY_VALUES
    ):

        raise ValueError(
            "Only the Highest Jira priority "
            "is allowed by the current tool policy."
        )

    # =====================================================
    # TRACE TOOL CALL
    # =====================================================

    trace_log(
        "TOOL_CALL",
        (
            "tool=update_jira_priority "
            f"issue={issue_key} "
            f"priority={priority_name}"
        )
    )

    logger.info(
        "JIRA TOOL CALL | "
        "tool=update_jira_priority | "
        "issue=%s | "
        "priority=%s",

        issue_key,

        priority_name
    )

    # =====================================================
    # JIRA SERVICE
    # =====================================================

    jira_service = (
        JiraService()
    )

    result = (
        jira_service
        .update_issue_priority(

            issue_key=issue_key,

            priority_name=priority_name
        )
    )

    # =====================================================
    # VERIFICATION
    # =====================================================

    mutation_verified = False

    if isinstance(
        result,
        dict
    ):

        mutation_verified = (
            result.get(
                "mutation_verified",
                False
            )
        )

    logger.info(
        "JIRA TOOL RESULT | "
        "tool=update_jira_priority | "
        "issue=%s | "
        "mutation_verified=%s",

        issue_key,

        mutation_verified
    )

    trace_log(
        "TOOL_RESULT",
        (
            "tool=update_jira_priority "
            f"issue={issue_key} "
            f"mutation_verified={mutation_verified}"
        )
    )

    return result