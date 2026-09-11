import logging
from typing import Any
from app.db.database import SessionLocal
from app.models.execution import WorkflowExecution

logger = logging.getLogger(__name__)

MIN_REQUIRED_EXECUTIONS = 5


class TrendForecastingService:
    """Trend Forecasting Engine (Phase 5.4 — #71)

    DEFERRED REQUIREMENT:
    Implement only after sufficient historical data is accumulated.
    Enables future bottleneck forecasting without blocking Phase 5 completion.
    """

    def __init__(self, min_required: int = MIN_REQUIRED_EXECUTIONS):
        self.min_required = min_required

    def get_forecast(self, db_session=None) -> dict[str, Any]:
        """Evaluates historical execution volume and produces a forecasting

        summary if sufficient data points exist; otherwise returns a graceful
        deferred status with zero invented metrics.
        """
        db = db_session or SessionLocal()
        should_close = db_session is None

        try:
            executions = (
                db.query(WorkflowExecution)
                .order_by(WorkflowExecution.started_at.desc())
                .limit(20)
                .all()
            )

            count = len(executions)

            # =====================================================
            # INSUFFICIENT DATA → GRACEFUL DEFERRAL
            # =====================================================
            if count < self.min_required:
                logger.info(
                    "TREND FORECASTING | DEFERRED | "
                    "available=%d | required=%d",
                    count,
                    self.min_required,
                )
                return {
                    "status": "deferred",
                    "feature": "Trend Forecasting (#71)",
                    "message": (
                        f"Trend forecasting requires at least {self.min_required} historical "
                        f"execution runs. Currently {count} recorded."
                    ),
                    "data_points_available": count,
                    "data_points_required": self.min_required,
                    "is_deferred": True,
                    "forecast": None,
                }

            # =====================================================
            # SUFFICIENT DATA → COMPUTE HISTORICAL TRAJECTORY
            # =====================================================
            recent = list(reversed(executions))  # chronological order
            issue_counts = [e.total_issues for e in recent]
            high_sev_counts = [e.high_severity_issues for e in recent]

            avg_issues = sum(issue_counts) / len(issue_counts)
            last_issues = issue_counts[-1]

            if last_issues > avg_issues * 1.2:
                issue_trend = "increasing"
            elif last_issues < avg_issues * 0.8:
                issue_trend = "decreasing"
            else:
                issue_trend = "stable"

            avg_high_sev = sum(high_sev_counts) / len(high_sev_counts)

            return {
                "status": "active",
                "feature": "Trend Forecasting (#71)",
                "message": (
                    f"Forecasting active with {count} historical execution records."
                ),
                "data_points_available": count,
                "data_points_required": self.min_required,
                "is_deferred": False,
                "forecast": {
                    "issue_volume_trend": issue_trend,
                    "avg_historical_issues": round(avg_issues, 1),
                    "avg_high_severity_issues": round(avg_high_sev, 1),
                    "trajectory_summary": (
                        f"Work item volume is currently {issue_trend} relative to the "
                        f"{round(avg_issues, 1)} historical baseline."
                    ),
                },
            }

        except Exception as e:
            logger.exception("Error evaluating trend forecasting: %s", e)
            return {
                "status": "deferred",
                "feature": "Trend Forecasting (#71)",
                "message": f"Trend forecasting temporarily unavailable: {e}",
                "data_points_available": 0,
                "data_points_required": self.min_required,
                "is_deferred": True,
                "forecast": None,
            }
        finally:
            if should_close:
                db.close()
