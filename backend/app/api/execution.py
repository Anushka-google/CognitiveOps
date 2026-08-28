from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.execution import (
    WorkflowExecution
)


# ==========================================
# Router
# ==========================================

router = APIRouter(
    prefix="/executions",
    tags=["Executions"]
)


# ==========================================
# Response Schema
# ==========================================

class ExecutionResponse(BaseModel):

    id: int

    started_at: datetime

    completed_at: datetime | None = None

    execution_time: float | None = None

    total_issues: int

    high_severity_issues: int

    workflow_health: str | None = None

    class Config:
        from_attributes = True


# ==========================================
# Get All Executions
# ==========================================

@router.get(
    "/",
    response_model=list[ExecutionResponse]
)
def get_executions(
    db: Session = Depends(get_db)
):

    executions = (
        db.query(WorkflowExecution)
        .order_by(
            WorkflowExecution.id.desc()
        )
        .all()
    )

    return executions


# ==========================================
# Get Single Execution
# ==========================================

@router.get(
    "/{execution_id}",
    response_model=ExecutionResponse
)
def get_execution(
    execution_id: int,
    db: Session = Depends(get_db)
):

    execution = (
        db.query(WorkflowExecution)
        .filter(
            WorkflowExecution.id == execution_id
        )
        .first()
    )

    if execution is None:

        raise HTTPException(
            status_code=404,
            detail="Execution not found"
        )

    return execution