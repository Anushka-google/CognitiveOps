from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.models.analytics import AnalyticsSnapshot

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def seed_historical_data_if_empty(self):
        """Seeds the last 30 days of analytics snapshots if the table is empty."""
        count = self.db.query(AnalyticsSnapshot).count()
        if count > 0:
            return

        today = datetime.utcnow()
        snapshots = []
        
        # Start 30 days ago, simulating improving trends over time
        for i in range(30, -1, -1):
            date = today - timedelta(days=i)
            
            # Simulated trends (e.g., getting better over time)
            improvement_factor = (30 - i) / 30.0 # 0.0 to 1.0
            
            snapshot = AnalyticsSnapshot(
                timestamp=date,
                avg_duration_days=max(2.5, 7.0 - (improvement_factor * 3.0) + random.uniform(-1, 1)),
                bottleneck_count=max(0, int(15 - (improvement_factor * 10) + random.randint(-3, 3))),
                high_risk_count=max(0, int(8 - (improvement_factor * 5) + random.randint(-2, 2))),
                sla_breach_rate=max(1.0, 15.0 - (improvement_factor * 10.0) + random.uniform(-2, 2)),
                team_velocity=int(20 + (improvement_factor * 15) + random.randint(-5, 5)),
                health_score=min(100.0, 60.0 + (improvement_factor * 35.0) + random.uniform(-5, 5))
            )
            snapshots.append(snapshot)
            
        self.db.bulk_save_objects(snapshots)
        self.db.commit()

    def get_dashboard_metrics(self):
        """Returns structured metrics for the 6 subparts."""
        self.seed_historical_data_if_empty()
        
        # Get last 30 days of data ordered chronologically
        history = self.db.query(AnalyticsSnapshot).order_by(AnalyticsSnapshot.timestamp.asc()).limit(30).all()
        
        if not history:
            return {}

        current = history[-1]
        previous = history[-2] if len(history) > 1 else current
        
        def calc_trend(curr, prev):
            if prev == 0: return 0
            return round(((curr - prev) / prev) * 100, 1)

        return {
            "duration": {
                "current": round(current.avg_duration_days, 1),
                "trend": calc_trend(current.avg_duration_days, previous.avg_duration_days),
                "unit": "days",
                "history": [round(h.avg_duration_days, 1) for h in history]
            },
            "bottlenecks": {
                "current": current.bottleneck_count,
                "trend": calc_trend(current.bottleneck_count, previous.bottleneck_count),
                "unit": "tickets stuck",
                "history": [h.bottleneck_count for h in history]
            },
            "risk": {
                "current": current.high_risk_count,
                "trend": calc_trend(current.high_risk_count, previous.high_risk_count),
                "unit": "high risk items",
                "history": [h.high_risk_count for h in history]
            },
            "sla": {
                "current": round(current.sla_breach_rate, 1),
                "trend": calc_trend(current.sla_breach_rate, previous.sla_breach_rate),
                "unit": "% breached",
                "history": [round(h.sla_breach_rate, 1) for h in history]
            },
            "team_performance": {
                "current": current.team_velocity,
                "trend": calc_trend(current.team_velocity, previous.team_velocity),
                "unit": "tickets resolved",
                "history": [h.team_velocity for h in history]
            },
            "trends": {
                "current": round(current.health_score, 1),
                "trend": calc_trend(current.health_score, previous.health_score),
                "unit": "health score",
                "history": [round(h.health_score, 1) for h in history],
                "dates": [h.timestamp.strftime("%b %d") for h in history]
            }
        }
