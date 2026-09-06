from datetime import datetime
import json

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float
)

from app.db.database import Base


class WorkflowExecution(Base):

    __tablename__ = "workflow_executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    started_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    execution_time = Column(
        Float,
        nullable=True
    )

    total_issues = Column(
        Integer,
        nullable=False,
        default=0
    )

    high_severity_issues = Column(
        Integer,
        nullable=False,
        default=0
    )

    workflow_health = Column(
        String,
        nullable=True
    )

    memory = Column(
        String,
        nullable=True
    )