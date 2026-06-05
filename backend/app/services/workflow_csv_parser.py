import csv

from app.models.workflow import (
    WorkflowRecord
)


def parse_workflow_csv(
    file_path: str
):

    workflows = []

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(
            file
        )

        for row in reader:

            workflow = WorkflowRecord(
                ticket_id=row["ticket_id"],
                assignee=row["assignee"],
                status=row["status"],
                days_waiting=int(
                    row["days_waiting"]
                )
            )

            workflows.append(
                workflow
            )

    return workflows