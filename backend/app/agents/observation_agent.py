import logging
import time

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


# =========================================================
# HELPERS
# =========================================================

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


def _normalize_evidence_items(value):
    """
    Normalize structured evidence into a list.

    Supported formats:

        Jira issue:
        {
            "key": "KAN-2",
            "fields": {...}
        }

        Jira issue list:
        [
            {...},
            {...}
        ]

        Jira search response:
        {
            "issues": [...]
        }

    This prevents a valid Jira dictionary from being
    incorrectly treated as empty evidence.
    """

    if value is None:
        return []

    # Already a collection of evidence items.
    if isinstance(
        value,
        (list, tuple, set)
    ):
        return list(value)

    # Structured dictionary.
    if isinstance(value, dict):

        # Jira search/API response containing issues.
        issues = value.get("issues")

        if isinstance(
            issues,
            list
        ):
            return issues

        # A single Jira issue is itself a dictionary.
        return [value]

    return []


def _extract_nested_value(item, *keys):
    """
    Safely retrieve a value from either:

        item["key"]

    or:

        item["fields"]["key"]
    """

    if not isinstance(
        item,
        dict
    ):
        return None

    fields = item.get(
        "fields",
        {}
    )

    if not isinstance(
        fields,
        dict
    ):
        fields = {}

    for key in keys:

        value = item.get(
            key
        )

        if value is not None:
            return value

        value = fields.get(
            key
        )

        if value is not None:
            return value

    return None


def _normalize_field_value(value):
    """
    Jira commonly returns fields such as:

        {"name": "In Progress"}

    Convert these into simple values.
    """

    if isinstance(
        value,
        dict
    ):

        # Jira status / priority / user etc.
        if value.get("name") is not None:
            return value.get("name")

        if value.get("value") is not None:
            return value.get("value")

        if value.get("displayName") is not None:
            return value.get(
                "displayName"
            )

        if value.get("key") is not None:
            return value.get(
                "key"
            )

    return value


def _has_value(value):
    """
    Determine whether a field actually contains
    useful evidence.
    """

    if value is None:
        return False

    if isinstance(
        value,
        str
    ):
        return bool(
            value.strip()
        )

    return True


# =========================================================
# OBSERVATION AGENT
# =========================================================

def observation_agent(
    state: AgentState
):
    """
    Observes evidence collected by previous agents.

    The agent validates whether the available Jira/Slack
    evidence is sufficient for downstream reasoning.

    Important:

    Jira API responses can be either:

        list[dict]

    or:

        dict

    representing one Jira issue.

    Therefore evidence is normalized before inspection.
    """

    logger.info(
        "AGENT START | observation_agent"
    )

    start_time = time.perf_counter()

    try:

        # =====================================================
        # READ JIRA EVIDENCE
        # =====================================================

        jira_evidence = state.get(
            "jira_evidence",
            []
        )

        # =====================================================
        # READ SLACK EVIDENCE
        # =====================================================

        slack_evidence = state.get(
            "slack_evidence",
            []
        )

        # =====================================================
        # FALLBACK TO COMBINED EVIDENCE
        # =====================================================

        combined_evidence = state.get(
            "combined_evidence",
            {}
        )

        if not jira_evidence:

            if isinstance(
                combined_evidence,
                dict
            ):

                jira_evidence = (
                    combined_evidence.get(
                        "jira",
                        []
                    )
                )

        if not slack_evidence:

            if isinstance(
                combined_evidence,
                dict
            ):

                slack_evidence = (
                    combined_evidence.get(
                        "slack",
                        []
                    )
                )

        # =====================================================
        # NORMALIZE EVIDENCE
        # =====================================================

        jira_items = (
            _normalize_evidence_items(
                jira_evidence
            )
        )

        slack_items = (
            _normalize_evidence_items(
                slack_evidence
            )
        )

        logger.info(
            "OBSERVATION | "
            "jira_items=%s | "
            "slack_items=%s",
            len(jira_items),
            len(slack_items)
        )

        # =====================================================
        # JIRA EVIDENCE ANALYSIS
        # =====================================================

        jira_ticket_found = False
        jira_status_found = False
        jira_timeline_found = False
        jira_priority_found = False
        jira_risk_found = False

        jira_observations = []

        for item in jira_items:

            if not isinstance(
                item,
                dict
            ):
                continue

            # -------------------------------------------------
            # Ticket / Issue Key
            # -------------------------------------------------

            issue_key = (
                item.get("key")
                or
                item.get("issue_key")
                or
                item.get("ticket_id")
            )

            if not issue_key:

                issue_key = (
                    _extract_nested_value(
                        item,
                        "key",
                        "issue_key",
                        "ticket_id"
                    )
                )

            if _has_value(
                issue_key
            ):
                jira_ticket_found = True

            # -------------------------------------------------
            # Status
            # -------------------------------------------------

            status = _extract_nested_value(
                item,
                "status",
                "state"
            )

            status = _normalize_field_value(
                status
            )

            if _has_value(
                status
            ):
                jira_status_found = True

            # -------------------------------------------------
            # Priority
            # -------------------------------------------------

            priority = _extract_nested_value(
                item,
                "priority"
            )

            priority = _normalize_field_value(
                priority
            )

            if _has_value(
                priority
            ):
                jira_priority_found = True

            # -------------------------------------------------
            # Timeline
            #
            # Jira commonly exposes created,
            # updated and duedate inside fields.
            # -------------------------------------------------

            created = _extract_nested_value(
                item,
                "created",
                "created_at"
            )

            updated = _extract_nested_value(
                item,
                "updated",
                "updated_at"
            )

            due_date = _extract_nested_value(
                item,
                "duedate",
                "due_date"
            )

            timeline_found = (
                _has_value(created)
                or
                _has_value(updated)
                or
                _has_value(due_date)
            )

            if timeline_found:
                jira_timeline_found = True

            # -------------------------------------------------
            # Risk
            #
            # Risk may already be present in processed
            # workflow evidence.
            # -------------------------------------------------

            risk = _extract_nested_value(
                item,
                "risk",
                "risk_score",
                "risk_level"
            )

            risk = _normalize_field_value(
                risk
            )

            if _has_value(
                risk
            ):
                jira_risk_found = True

            # -------------------------------------------------
            # Store normalized observation
            # -------------------------------------------------

            jira_observations.append({

                "issue_key":
                    issue_key,

                "status":
                    status,

                "priority":
                    priority,

                "created":
                    created,

                "updated":
                    updated,

                "duedate":
                    due_date,

                "risk":
                    risk
            })

            logger.debug(
                "JIRA OBSERVATION | "
                "issue=%s | "
                "status=%s | "
                "priority=%s | "
                "created=%s | "
                "updated=%s | "
                "duedate=%s",
                issue_key,
                status,
                priority,
                created,
                updated,
                due_date
            )

        # =====================================================
        # SLACK EVIDENCE ANALYSIS
        # =====================================================

        slack_message_found = False
        slack_timeline_found = False

        slack_observations = []

        for item in slack_items:

            # -------------------------------------------------
            # Slack may contain structured dictionaries.
            # -------------------------------------------------

            if isinstance(
                item,
                dict
            ):

                message = (
                    item.get("message")
                    or
                    item.get("text")
                    or
                    item.get("content")
                )

                timestamp = (
                    item.get("timestamp")
                    or
                    item.get("ts")
                    or
                    item.get("created")
                    or
                    item.get("created_at")
                )

                if _has_value(
                    message
                ):
                    slack_message_found = True

                if _has_value(
                    timestamp
                ):
                    slack_timeline_found = True

                slack_observations.append({

                    "message":
                        message,

                    "timestamp":
                        timestamp
                })

            # -------------------------------------------------
            # Plain text Slack evidence.
            # -------------------------------------------------

            elif isinstance(
                item,
                str
            ):

                if item.strip():

                    slack_message_found = True

                    slack_observations.append({

                        "message":
                            item,

                        "timestamp":
                            None
                    })

        # =====================================================
        # EVIDENCE QUALITY
        # =====================================================

        evidence_quality = {

            "jira_ticket":
                jira_ticket_found,

            "jira_status":
                jira_status_found,

            "jira_timeline":
                jira_timeline_found,

            "jira_priority":
                jira_priority_found,

            "jira_risk":
                jira_risk_found,

            "slack_message":
                slack_message_found,

            "slack_timeline":
                slack_timeline_found
        }

        # =====================================================
        # DETERMINE SUFFICIENCY
        # =====================================================
        #
        # Jira alone is sufficient when we have:
        #
        #   ticket + status + timeline
        #
        # Slack is supplementary evidence.
        #
        # We do NOT require Slack to be present because
        # Slack evidence can legitimately be unavailable.
        # =====================================================

        jira_sufficient = (
            jira_ticket_found
            and
            jira_status_found
            and
            jira_timeline_found
        )

        slack_sufficient = (
            slack_message_found
            and
            slack_timeline_found
        )

        sufficient = (
            jira_sufficient
            or
            slack_sufficient
        )

        # =====================================================
        # OBSERVATION
        # =====================================================

        observation = {

            "sufficient":
                sufficient,

            "jira_count":
                len(jira_items),

            "slack_count":
                len(slack_items),

            "evidence_quality":
                evidence_quality,

            "jira_observations":
                jira_observations,

            "slack_observations":
                slack_observations,

            "summary":
                (
                    "Sufficient Jira evidence available."
                    if jira_sufficient
                    else
                    "Sufficient Slack evidence available."
                    if slack_sufficient
                    else
                    "Evidence is insufficient for reliable reasoning."
                )
        }

        # =====================================================
        # EXECUTION STATUS
        # =====================================================

        execution_status = state.get(
            "execution_status"
        )

        # HITL must remain paused.
        #
        # Observation must never accidentally turn
        # awaiting_human_approval into running/completed.
        if execution_status == (
            "awaiting_human_approval"
        ):

            logger.info(
                "OBSERVATION | "
                "HITL state preserved"
            )

        # =====================================================
        # STRUCTURED AGENT OUTPUT
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
            "observation_agent"
        ] = {

            "agent":
                "observation_agent",

            "status":
                "success",

            "output":
                observation,

            "execution_time":
                execution_time,

            "error":
                None
        }

        # =====================================================
        # FINAL STATE UPDATE
        # =====================================================

        state_update = {

            "observation":
                observation,

            "agent_outputs":
                agent_outputs
        }

        # -----------------------------------------------------
        # Preserve HITL status explicitly.
        # -----------------------------------------------------

        if execution_status == (
            "awaiting_human_approval"
        ):

            state_update[
                "execution_status"
            ] = (
                "awaiting_human_approval"
            )

            state_update[
                "goal_completed"
            ] = False

            state_update[
                "termination_reason"
            ] = (
                "human_approval_required"
            )

        logger.info(
            "OBSERVATION COMPLETE | "
            "sufficient=%s | "
            "jira_count=%s | "
            "slack_count=%s",
            sufficient,
            len(jira_items),
            len(slack_items)
        )

        logger.info(
            "AGENT END | observation_agent"
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
            "AGENT FAILED | observation_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        agent_outputs = (
            _copy_agent_outputs(
                state
            )
        )

        agent_outputs[
            "observation_agent"
        ] = {

            "agent":
                "observation_agent",

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
                "observation_agent",

            "error":
                str(e)
        })

        return {

            "agent_outputs":
                agent_outputs,

            "errors":
                errors,

            "execution_error":
                str(e)
        }