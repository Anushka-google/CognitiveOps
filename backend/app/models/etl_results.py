from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.db.database import Base

class ETLAnalyticsResult(Base):
    __tablename__ = "etl_analytics_results"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, index=True)
    avg_duration = Column(Float, default=0.0)
    avg_waiting_time = Column(Float, default=0.0)
    blocker_density = Column(Float, default=0.0)
    high_risk_workflows = Column(Integer, default=0)
    total_workflows = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
