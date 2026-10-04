import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.slack_service import SlackService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


class SlackConfig(BaseModel):
    webhook_url: Optional[str] = Field(None, description="Slack Incoming Webhook URL")
    bot_token: Optional[str] = Field(None, description="Slack Bot OAuth Token (xoxb-...)")
    channel_id: Optional[str] = Field(None, description="Slack Channel ID for notifications")


class AlertRequest(BaseModel):
    ticket_id: str = Field(..., example="KAN-101")
    title: str = Field(..., example="Deployment blocked due to auth bug")
    status: str = Field("Blocked", example="Blocked")
    priority: str = Field("High", example="High")
    impact_summary: str = Field(..., example="Workflow delayed by 4 days, impacting SLA timeline.")
    action_required: Optional[str] = Field("Manual Review Required", example="Review in Jira")


class ChannelMessageRequest(BaseModel):
    message: str = Field(..., example="🚨 Critical SLA Breach detected on KAN-101")


@router.post("/config", summary="Save Slack Configuration")
def save_slack_config(config: SlackConfig, current_user: User = Depends(get_current_user)):
    """Configure or update Slack credentials in runtime environment."""
    if config.webhook_url:
        os.environ["SLACK_WEBHOOK_URL"] = config.webhook_url
    if config.bot_token:
        os.environ["SLACK_BOT_TOKEN"] = config.bot_token
    if config.channel_id:
        os.environ["SLACK_CHANNEL_ID"] = config.channel_id

    return {
        "success": True,
        "message": "Slack configuration updated successfully!",
        "configured_items": {
            "has_webhook": bool(os.getenv("SLACK_WEBHOOK_URL")),
            "has_bot_token": bool(os.getenv("SLACK_BOT_TOKEN")),
            "has_channel": bool(os.getenv("SLACK_CHANNEL_ID"))
        }
    }


@router.get("/status", summary="Slack Connection Status")
def slack_status():
    """Check connectivity and credentials for Slack workspace."""
    service = SlackService()
    status = service.get_status()
    return {
        "integration": "Slack",
        "connected": status["configured"],
        "details": status
    }


@router.post("/alert", summary="Send Structured Incident Alert")
def send_slack_alert(alert: AlertRequest, current_user: User = Depends(get_current_user)):
    """Dispatch an incident Block Kit alert card directly to the engineering channel."""
    service = SlackService()
    result = service.send_incident_card(
        ticket_id=alert.ticket_id,
        title=alert.title,
        status=alert.status,
        priority=alert.priority,
        impact_summary=alert.impact_summary,
        action_required=alert.action_required or "Review in Jira"
    )
    return {"success": True, "result": result}


@router.post("/message", summary="Send Quick Message")
def send_simple_message(request: ChannelMessageRequest, current_user: User = Depends(get_current_user)):
    """Send a quick broadcast message to Slack channel."""
    service = SlackService()
    status_code = service.send_alert(request.message)
    return {"success": status_code in [200, 201], "status_code": status_code}


@router.get("/evidence/{ticket_id}", summary="Harvest Ticket Evidence from Slack")
def get_slack_evidence(ticket_id: str, current_user: User = Depends(get_current_user)):
    """Fetch discussions and mentions of a ticket from Slack communication channels."""
    service = SlackService()
    evidence = service.get_ticket_evidence(ticket_id)
    return {
        "ticket_id": ticket_id,
        "count": len(evidence),
        "evidence": evidence
    }


@router.post("/test", summary="Test Connection")
def slack_test():
    """Verify communication with configured Slack workspace."""
    service = SlackService()
    status = service.get_status()
    if status["configured"]:
        return {
            "success": True,
            "message": "Slack workspace integration verified! Ready for live alerts.",
            "details": status
        }
    return {
        "success": False,
        "message": "Slack credentials not configured. Please supply SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN."
    }
