from pydantic import BaseModel


class Insight(BaseModel):
    issue: str
    evidence: list[str]
    severity: str
    root_cause: str | None = None
    impact: str | None = None
    recommendation: str | None = None