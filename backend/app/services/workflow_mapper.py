from app.models.workflow import (
    WorkflowRecord
)


def map_jira_to_workflow(
    ticket
):

    return WorkflowRecord(
        ticket_id=str(
            ticket["id"]
        ),

        assignee="Unknown",

        status="Open",

        days_waiting=5
    )