from datetime import datetime, timezone

from app.models.workflow import WorkflowRecord


def map_jira_to_workflow(ticket):

    fields = ticket.get("fields", {})

    assignee = fields.get("assignee")

    assignee_name = (
        assignee.get("displayName")
        if assignee
        else "Unassigned"
    )

    status = (
        fields.get("status", {})
        .get("name", "Unknown")
    )

    created = fields.get("created")

    days_waiting = 0

    if created:
        created_dt = datetime.fromisoformat(
            created.replace("Z", "+00:00")
        )

        days_waiting = (
            datetime.now(timezone.utc)
            - created_dt
        ).days

    return WorkflowRecord(
        ticket_id=ticket["key"],
        assignee=assignee_name,
        status=status,
        days_waiting=days_waiting
    )