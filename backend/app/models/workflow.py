from pydantic import BaseModel


class WorkflowRecord(BaseModel):
    ticket_id: str
    assignee: str
    status: str
    days_waiting: int
   