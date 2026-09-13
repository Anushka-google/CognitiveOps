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

from app.services.spark_analytics_service import SparkAnalyticsService

router = APIRouter()

@router.get("/status")
def reports_status():
    return {"message": "Reports API is reachable."}

@router.get(
    "/spark-etl",
    summary="Phase 7: End-to-End PySpark ETL Pipeline",
    description="Extracts raw data, Cleans, Transforms Features, Aggregates, and Loads to Database."
)
def run_spark_etl():
    try:
        spark_service = SparkAnalyticsService()
        results = spark_service.execute_full_etl_pipeline()
        return results
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
        risk_data = risk_service.calculate(tickets)
        risks = risk_data.get("tickets", [])
    except Exception as e:
        print(f"Error exporting risks: {e}")
        risks = []
        
    headers = ["Ticket ID", "Risk Score", "Risk Level", "Recommendation"]
    rows = [[r.get("ticket_id", ""), r.get("risk_score", ""), r.get("risk_level", ""), r.get("recommendation", "")] for r in risks]
    
    return _create_csv_response("risks", headers, rows)


@router.get("/export/insights")
def export_insights():
    try:
        jira_service = JiraService()
        tickets = jira_service.get_workflow_records()
        
        exec_service = ExecutiveIntelligenceService()
        summary = exec_service.generate_summary(
            workflows=tickets,
            root_cause_graph={"nodes": [], "edges": [], "root_causes": []},
            sla_prediction={},
            workflow_health="Unknown"
        ) 
        insights = summary.get("why", [])
    except Exception as e:
        print(f"Error exporting insights: {e}")
        insights = []
        
    headers = ["Insight Type", "Description"]
    rows = [["Root Cause / Insight", str(i)] for i in insights]
    
    return _create_csv_response("insights", headers, rows)


@router.get("/export/recommendations")
def export_recommendations():
    try:
        jira_service = JiraService()
        tickets = jira_service.get_workflow_records()
        
        exec_service = ExecutiveIntelligenceService()
        summary = exec_service.generate_summary(
            workflows=tickets,
            root_cause_graph={"nodes": [], "edges": [], "root_causes": []},
            sla_prediction={},
            workflow_health="Unknown"
        ) 
        recommendations = summary.get("what_should_we_do", [])
    except Exception as e:
        print(f"Error exporting recommendations: {e}")
        recommendations = []
        
    headers = ["Action Item", "Description"]
    rows = [["Recommended Action", str(r)] for r in recommendations]
    
    return _create_csv_response("recommendations", headers, rows)

