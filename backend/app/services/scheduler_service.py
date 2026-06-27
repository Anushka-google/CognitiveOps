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


def run_analysis():

    print(
        "Running Scheduled Analysis..."
    )

    jira_service = (
        JiraService()
    )

    workflows = (
        jira_service.get_workflow_records()
    )

    graph_service = (
        WorkflowGraphService()
    )

    result = (
        graph_service.analyze(
            workflows
        )
    )

    insights = result.get(
        "insights",
        []
    )

    slack_service = (
        SlackService()
    )
    slack_service.send_alert(
    "🚀 Scheduler Test Success"
)

    for insight in insights:

        if (
            insight.severity
            == "High"
        ):

            message = f"""
🚨 CognitiveOps Alert

Issue:
{insight.issue}

Severity:
{insight.severity}

Evidence:
{insight.evidence[0]}
"""

            slack_service.send_alert(
                message
            )

            break

    print(
        result["workflow_health"]
    )


scheduler = (
    BackgroundScheduler()
)

from datetime import (
    datetime,
    timedelta
)

scheduler.add_job(
    run_analysis,
    "interval",
    minutes=1,
    next_run_time=
        datetime.now()
        + timedelta(seconds=10)
)

