from datetime import datetime
from app.models.workflow import WorkflowRecord


def map_jira_to_workflow(ticket):
    fields = ticket["fields"]

    created = datetime.fromisoformat(
        fields["created"].replace("Z", "+00:00")
    )

    days_waiting = (
        datetime.now(created.tzinfo) - created
    ).days

    return WorkflowRecord(
        ticket_id=ticket["key"],
        title=fields["summary"],
        status=fields["status"]["name"],
        priority=(
            fields["priority"]["name"]
            if fields["priority"]
            else "Unknown"
        ),
        assignee=(
            fields["assignee"]["displayName"]
            if fields["assignee"]
            else "Unassigned"
        ),
        due_date=fields["duedate"],
        created_at=fields["created"],
        days_waiting=days_waiting
    )