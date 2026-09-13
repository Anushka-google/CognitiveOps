from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime
from app.db.database import Base

class AnalyticsSnapshot(Base):
    """
    OLAP-style Fact Table storing pre-computed daily metrics for the Analytics Dashboard.
    """
    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # 1. Duration (How long tickets take)
    avg_duration_days = Column(Float, nullable=False, default=0.0)
    
    # 2. Bottlenecks (Where tickets get stuck)
    bottleneck_count = Column(Integer, nullable=False, default=0)
    
    # 3. Risk (Risk trends over time)
    high_risk_count = Column(Integer, nullable=False, default=0)
    
    # 4. SLA (SLA breach rates)
    sla_breach_rate = Column(Float, nullable=False, default=0.0)
    
    # 5. Team Performance (Velocity)
    team_velocity = Column(Integer, nullable=False, default=0)
    
    # 6. Trends (Overall health score 0-100)
    health_score = Column(Float, nullable=False, default=100.0)
