import logging

from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.services.slack_service import (
    SlackService
)

from app.services.jira_service import (
    JiraService
)

from app.services.workflow_graph_service import (
    WorkflowGraphService
)

from app.services.trace_service import (
    trace_log,
    clear_trace_context
)

from datetime import (
    datetime,
    timedelta
)


logger = logging.getLogger(__name__)


# =========================================================
# SCHEDULED ANALYSIS
# =========================================================

def run_analysis():

    trace_log(
        "SCHEDULED_ANALYSIS_START"
    )

    print(
        "Running Scheduled Analysis..."
    )

    try:

        # =================================================
        # JIRA
        # =================================================

        jira_service = (
            JiraService()
        )

        workflows = (
            jira_service
            .get_workflow_records()
        )

        trace_log(
            "SCHEDULED_DATA_RETRIEVED",
            (
                f"workflow_count="
                f"{len(workflows)}"
            )
        )

        # =================================================
        # WORKFLOW GRAPH
        # =================================================

        graph_service = (
            WorkflowGraphService()
        )

        result = (
            graph_service.analyze(
                workflows
            )
        )

        # =================================================
        # SLACK ALERTS
        # =================================================

        insights = result.get(
            "insights",
            []
        )

        slack_service = (
            SlackService()
        )

        high_severity_count = 0

        for insight in insights:

            if (
                insight.severity
                == "High"
            ):

                high_severity_count += 1

                evidence = (
                    insight.evidence
                    if getattr(
                        insight,
                        "evidence",
                        None
                    )
                    else []
                )

                evidence_text = (
                    evidence[0]
                    if evidence
                    else "No evidence available."
                )

                message = f"""
🚨 CognitiveOps Alert

Issue:
{insight.issue}

Severity:
{insight.severity}

Evidence:
{evidence_text}
"""

                slack_service.send_alert(
                    message
                )

        trace_log(
            "SCHEDULED_ALERTS_PROCESSED",
            (
                f"high_severity_count="
                f"{high_severity_count}"
            )
        )

        print(
            result.get(
                "workflow_health"
            )
        )

        trace_log(
            "SCHEDULED_ANALYSIS_END",
            (
                f"execution_id="
                f"{result.get('execution_id')} "
                f"workflow_health="
                f"{result.get('workflow_health')}"
            )
        )

        return result

    except Exception as e:

        logger.exception(
            "SCHEDULED ANALYSIS FAILED | %s",
            e
        )

        trace_log(
            "SCHEDULED_ANALYSIS_FAILED",
            str(e),
            logging.ERROR
        )

        raise

    finally:

        clear_trace_context()


# =========================================================
# SCHEDULER
# =========================================================

scheduler = (
    BackgroundScheduler()
)


scheduler.add_job(
    run_analysis,
    "interval",
    minutes=1,
    next_run_time=
        datetime.now()
        + timedelta(
            seconds=10
        )
)