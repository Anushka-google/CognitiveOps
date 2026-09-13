from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv
from datetime import datetime

from app.db.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.jira_service import JiraService
from app.services.risk_scoring_service import RiskScoringService
from app.services.executive_intelligence_service import ExecutiveIntelligenceService

router = APIRouter()

@router.get("/status")
def reports_status():
    return {"message": "Reports API is reachable."}

@router.get(
    "/analytics/dashboard",
    summary="Get Historical Analytics",
    description="Retrieves OLAP pre-computed metrics for Duration, Bottlenecks, Risk, SLA, Velocity, and Trends over the last 30 days."
)
def get_analytics_dashboard(db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return service.get_dashboard_metrics()

# ==========================================
# CSV EXPORT ENDPOINTS
# ==========================================

def _create_csv_response(filename: str, headers: list, rows: list):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    stream.seek(0)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}_{datetime.now().strftime('%Y%m%d')}.csv"
    return response


@router.get("/export/workflows")
def export_workflows():
    try:
        jira_service = JiraService()
        tickets = jira_service.get_workflow_records()
    except Exception:
        tickets = [] # Fallback if no Jira connection
        
    headers = ["Ticket ID", "Title", "Status", "Priority", "Assignee", "Days Waiting"]
    rows = [[t.ticket_id, t.title, t.status, t.priority, t.assignee, t.days_waiting] for t in tickets]
    
    return _create_csv_response("workflows", headers, rows)


@router.get("/export/risks")
def export_risks():
    try:
        risk_service = RiskScoringService()
        jira_service = JiraService()
        tickets = jira_service.get_workflow_records()
        risks = risk_service.get_risk_scores(tickets)
    except Exception:
        risks = []
        
    headers = ["Ticket ID", "Risk Score", "Risk Level", "Factors"]
    rows = [[r.ticket_id, r.score, r.risk_level, ", ".join(r.factors)] for r in risks]
    
    return _create_csv_response("risks", headers, rows)


@router.get("/export/insights")
def export_insights():
    try:
        exec_service = ExecutiveIntelligenceService()
        # Passing an empty list just to trigger the mock summary for the export
        summary = exec_service.generate_executive_summary([]) 
        insights = summary.get("insights", [])
    except Exception:
        insights = []
        
    headers = ["Category", "Insight Description", "Severity"]
    rows = [[i.get("category", "General"), i.get("description", ""), i.get("severity", "medium")] for i in insights]
    
    return _create_csv_response("insights", headers, rows)


@router.get("/export/recommendations")
def export_recommendations():
    try:
        exec_service = ExecutiveIntelligenceService()
        summary = exec_service.generate_executive_summary([]) 
        recommendations = summary.get("recommendations", [])
    except Exception:
        recommendations = []
        
    headers = ["Action Item", "Expected Impact", "Effort"]
    rows = [[r.get("action", ""), r.get("impact", ""), r.get("effort", "")] for r in recommendations]
    
    return _create_csv_response("recommendations", headers, rows)

