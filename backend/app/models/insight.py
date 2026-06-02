from pydantic import BaseModel


class Insight(BaseModel):
    issue: str
    evidence: list[str]
    severity: str

    impact: str | None = None
    recommendation: str | None = None