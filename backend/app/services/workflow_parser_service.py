from app.models.workflow import (
    WorkflowRecord
)


def parse_workflow_text(
    text: str
):

    workflows = []

    lines = text.splitlines()

    for line in lines:

        parts = line.split(",")

        if len(parts) != 4:
            continue

        workflow = WorkflowRecord(
            ticket_id=parts[0].strip(),
            assignee=parts[1].strip(),
            status=parts[2].strip(),
            days_waiting=int(
                parts[3].strip()
            )
        )

        workflows.append(
            workflow
        )

    return workflows