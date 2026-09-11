from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ExecutiveKPIs(BaseModel):
    workflow_health: str
    total_tickets: int
    delayed_tickets_count: int
    high_severity_issues_count: int
    avg_days_waiting: float
    max_days_waiting: float
    sla_breach_probability: float
    sla_risk_level: str
    active_blockers_count: int


class CriticalBlocker(BaseModel):
    blocker_key: str
    blocked_key: str
    relationship: str
    description: str | None = None


class ExecutiveSummary(BaseModel):
    title: str = "Executive Intelligence Summary"
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    kpis: ExecutiveKPIs
    what_happened: list[str]
    why: list[str]
    what_should_we_do: list[str]
    primary_bottleneck: str
    critical_blockers: list[CriticalBlocker] = []
    data_grounding_verified: bool = True
