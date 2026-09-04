import json
import logging
from datetime import datetime
from typing import Any


from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from pydantic import BaseModel

from sqlalchemy.orm import Session


from app.db.database import (
    get_db
)

from app.models.execution import (
    WorkflowExecution
)

from app.services.jira_service import (
    JiraService
)


logger = logging.getLogger(__name__)


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

    execution_status: str | None = None

    approval_required: bool = False

    approval_status: str | None = None

    proposed_action: dict[str, Any] | None = None

    # ------------------------------------------
    # HITL / Audit information
    # ------------------------------------------

    approved_at: str | None = None

    rejected_at: str | None = None

    termination_reason: str | None = None

    approved_action_result: dict[str, Any] | None = None

    class Config:

        from_attributes = True


# ==========================================
# Helpers
# ==========================================

def _extract_memory(
    execution
):

    memory = getattr(
        execution,
        "memory",
        None
    )

    if memory is None:

        return {}

    if isinstance(
        memory,
        dict
    ):

        return memory

    if isinstance(
        memory,
        str
    ):

        try:

            parsed = json.loads(
                memory
            )

            if isinstance(
                parsed,
                dict
            ):

                return parsed

            return {}

        except Exception:

            return {}

    return {}


def _build_execution_response(
    execution
):

    memory = _extract_memory(
        execution
    )

    return {

        "id":
            execution.id,

        "started_at":
            execution.started_at,

        "completed_at":
            execution.completed_at,

        "execution_time":
            execution.execution_time,

        "total_issues":
            execution.total_issues,

        "high_severity_issues":
            execution.high_severity_issues,

        "workflow_health":
            execution.workflow_health,

        "execution_status":
            memory.get(
                "execution_status"
            ),

        "approval_required":
            memory.get(
                "approval_required",
                False
            ),

        "approval_status":
            memory.get(
                "approval_status"
            ),

        "proposed_action":
            memory.get(
                "proposed_action"
            ),

        # --------------------------------------
        # HITL / Audit information
        # --------------------------------------

        "approved_at":
            memory.get(
                "approved_at"
            ),

        "rejected_at":
            memory.get(
                "rejected_at"
            ),

        "termination_reason":
            memory.get(
                "termination_reason"
            ),

        "approved_action_result":
            memory.get(
                "approved_action_result"
            )
    }


# ==========================================
# Get All Executions
# ==========================================

@router.get(
    "/",
    response_model=list[ExecutionResponse]
)
def get_executions(

    offset: int = 0,

    limit: int = 20,

    db: Session = Depends(
        get_db
    )
):

    executions = (

        db.query(
            WorkflowExecution
        )

        .order_by(
            WorkflowExecution.id.desc()
        )

        .offset(
            offset
        )

        .limit(
            limit
        )

        .all()
    )

    return [

        _build_execution_response(
            execution
        )

        for execution in executions
    ]


# ==========================================
# Pending Human Approval
# ==========================================

@router.get(
    "/pending-approval"
)
def get_pending_approval(

    db: Session = Depends(
        get_db
    )
):

    executions = (

        db.query(
            WorkflowExecution
        )

        .order_by(
            WorkflowExecution.id.desc()
        )

        .limit(
            50
        )

        .all()
    )

    for execution in executions:

        memory = _extract_memory(
            execution
        )

        if (

            memory.get(
                "execution_status"
            )
            ==
            "awaiting_human_approval"

            and

            memory.get(
                "approval_required",
                False
            )

            and

            memory.get(
                "approval_status"
            )
            ==
            "pending"
        ):

            return {

                "execution_id":
                    execution.id,

                "execution_status":
                    memory.get(
                        "execution_status"
                    ),

                "approval_required":
                    True,

                "approval_status":
                    "pending",

                "approval_reason":
                    memory.get(
                        "approval_reason"
                    ),

                "proposed_action":
                    memory.get(
                        "proposed_action"
                    )
            }

    return {

        "execution_id":
            None,

        "execution_status":
            None,

        "approval_required":
            False,

        "approval_status":
            None,

        "approval_reason":
            None,

        "proposed_action":
            None
    }


# ==========================================
# APPROVE HUMAN-IN-THE-LOOP ACTION
# ==========================================

@router.post(
    "/{execution_id}/approve"
)
def approve_execution(

    execution_id: int,

    db: Session = Depends(
        get_db
    )
):

    execution = (

        db.query(
            WorkflowExecution
        )

        .filter(
            WorkflowExecution.id
            ==
            execution_id
        )

        .first()
    )

    if execution is None:

        raise HTTPException(

            status_code=404,

            detail="Execution not found"
        )

    memory = _extract_memory(
        execution
    )

    approval_status = memory.get(
        "approval_status"
    )

    execution_status = memory.get(
        "execution_status"
    )

    proposed_action = memory.get(
        "proposed_action"
    ) or {}

    # ==========================================
    # Safety validation
    # ==========================================

    if approval_status != "pending":

        raise HTTPException(

            status_code=400,

            detail=(
                "This execution is not "
                "waiting for approval."
            )
        )

    if execution_status != (
        "awaiting_human_approval"
    ):

        raise HTTPException(

            status_code=400,

            detail=(
                "Execution is not in "
                "human approval state."
            )
        )

    action_type = proposed_action.get(
        "action_type"
    )

    if action_type != (
        "jira_update_priority"
    ):

        raise HTTPException(

            status_code=400,

            detail=(
                "Unsupported high-impact "
                "action."
            )
        )

    issue_key = proposed_action.get(
        "target"
    )

    priority_name = proposed_action.get(
        "new_value",
        "Highest"
    )

    if not issue_key:

        raise HTTPException(

            status_code=400,

            detail=(
                "No Jira issue key found "
                "in proposed action."
            )
        )

    # ==========================================
    # HUMAN APPROVED
    # ==========================================

    logger.warning(

        "HUMAN APPROVAL RECEIVED | "
        "execution_id=%s | "
        "action=%s | "
        "issue=%s",

        execution_id,
        action_type,
        issue_key
    )

    try:

        jira_service = JiraService()

        result = (

            jira_service
            .update_issue_priority(
                issue_key,
                priority_name
            )
        )

    except Exception as e:

        logger.exception(

            "APPROVED JIRA ACTION FAILED | "
            "execution_id=%s",

            execution_id
        )

        memory[
            "approval_status"
        ] = "approved"

        memory[
            "execution_status"
        ] = "failed"

        memory[
            "execution_error"
        ] = str(e)

        execution.memory = memory

        db.commit()

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )

    # ==========================================
    # Persist successful action
    # ==========================================

    memory[
        "approval_status"
    ] = "approved"

    memory[
        "approval_required"
    ] = False

    memory[
        "execution_status"
    ] = "completed"

    memory[
        "goal_completed"
    ] = True

    memory[
        "termination_reason"
    ] = "human_approved_action_executed"

    memory[
        "approved_action_result"
    ] = result

    memory[
        "approved_at"
    ] = datetime.utcnow().isoformat()

    execution.memory = memory

    execution.completed_at = (
        datetime.utcnow()
    )

    db.commit()

    db.refresh(
        execution
    )

    logger.info(

        "APPROVED ACTION EXECUTED | "
        "execution_id=%s | "
        "issue=%s | "
        "priority=%s",

        execution_id,
        issue_key,
        priority_name
    )

    return {

        "status":
            "success",

        "message":
            "Human-approved Jira action executed.",

        "execution_id":
            execution_id,

        "action":
            result
    }


# ==========================================
# REJECT HUMAN-IN-THE-LOOP ACTION
# ==========================================

@router.post(
    "/{execution_id}/reject"
)
def reject_execution(

    execution_id: int,

    db: Session = Depends(
        get_db
    )
):

    execution = (

        db.query(
            WorkflowExecution
        )

        .filter(
            WorkflowExecution.id
            ==
            execution_id
        )

        .first()
    )

    if execution is None:

        raise HTTPException(

            status_code=404,

            detail="Execution not found"
        )

    memory = _extract_memory(
        execution
    )

    if memory.get(
        "approval_status"
    ) != "pending":

        raise HTTPException(

            status_code=400,

            detail=(
                "Execution is not "
                "awaiting approval."
            )
        )

    memory[
        "approval_status"
    ] = "rejected"

    memory[
        "approval_required"
    ] = False

    memory[
        "execution_status"
    ] = "terminated"

    memory[
        "goal_completed"
    ] = False

    memory[
        "termination_reason"
    ] = "human_rejected"

    memory[
        "approval_reason"
    ] = (
        "Human rejected the "
        "proposed Jira action."
    )

    memory[
        "rejected_at"
    ] = datetime.utcnow().isoformat()

    execution.memory = memory

    execution.completed_at = (
        datetime.utcnow()
    )

    db.commit()

    logger.warning(

        "HUMAN ACTION REJECTED | "
        "execution_id=%s",

        execution_id
    )

    return {

        "status":
            "rejected",

        "message":
            "Human rejected the proposed action.",

        "execution_id":
            execution_id
    }


# ==========================================
# Get Single Execution
# ==========================================

@router.get(
    "/{execution_id}",
    response_model=ExecutionResponse
)
def get_execution(

    execution_id: int,

    db: Session = Depends(
        get_db
    )
):

    execution = (

        db.query(
            WorkflowExecution
        )

        .filter(
            WorkflowExecution.id
            ==
            execution_id
        )

        .first()
    )

    if execution is None:

        raise HTTPException(

            status_code=404,

            detail="Execution not found"
        )

    return _build_execution_response(
        execution
    )


# ==========================================
# Execution Statistics
# ==========================================

@router.get(
    "/stats/summary"
)
def get_execution_stats(

    db: Session = Depends(
        get_db
    )
):

    executions = (

        db.query(
            WorkflowExecution
        )

        .all()
    )

    total_executions = len(
        executions
    )

    execution_times = [

        execution.execution_time

        for execution in executions

        if execution.execution_time
        is not None
    ]

    average_execution_time = (

        sum(execution_times)
        /
        len(execution_times)

        if execution_times

        else 0
    )

    poor_executions = sum(

        1

        for execution in executions

        if execution.workflow_health
        ==
        "Poor"
    )

    total_high_severity_issues = sum(

        execution.high_severity_issues
        or 0

        for execution in executions
    )

    return {

        "total_executions":
            total_executions,

        "average_execution_time":
            round(
                average_execution_time,
                2
            ),

        "poor_executions":
            poor_executions,

        "total_high_severity_issues":
            total_high_severity_issues
    }