from datetime import datetime
from app.models.workflow import WorkflowRecord


def map_jira_to_workflow(ticket):

    fields = ticket["fields"]

    created_str = fields["created"]

    created = datetime.fromisoformat(
        created_str.replace(
            "Z",
            "+00:00"
        )
    )

    days_waiting = (
        datetime.now(
            created.tzinfo
        ) - created
    ).days

    return WorkflowRecord(
        ticket_id=ticket["key"],

        title=fields.get(
            "summary",
            "No Title"
        ),

        status=(
            fields["status"]["name"]
            if fields.get("status")
            else "Unknown"
        ),

        priority=(
            fields["priority"]["name"]
            if fields.get("priority")
            else "Unknown"
        ),

        assignee=(
            fields["assignee"]["displayName"]
            if fields.get("assignee")
            else "Unassigned"
        ),

        due_date=fields.get(
            "duedate"
        ),

        created_at=created_str,

        days_waiting=days_waiting
    )