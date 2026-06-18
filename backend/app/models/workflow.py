from pydantic import BaseModel
from typing import Optional


class WorkflowRecord(BaseModel):
    ticket_id: str
    title: str
    status: str
    priority: str
    assignee: str
    due_date: Optional[str] = None
    created_at: str
    days_waiting: int