from pydantic import BaseModel


class RiskScore(BaseModel):
    ticket_id: str
    risk_score: float
    risk_level: str