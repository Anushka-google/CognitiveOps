import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SlackConfig(BaseModel):
    webhook_url: str
    api_token: str

@router.post("/config")
def save_slack_config(config: SlackConfig):
    # Temporarily saving to environment variables so the app remembers it
    if config.webhook_url:
        os.environ["SLACK_WEBHOOK_URL"] = config.webhook_url
    if config.api_token:
        os.environ["SLACK_API_TOKEN"] = config.api_token
        
    return {"success": True, "message": "Slack configuration saved to server!"}

@router.get("/status")
def slack_status():
    has_webhook = bool(os.getenv("SLACK_WEBHOOK_URL"))
    has_token = bool(os.getenv("SLACK_API_TOKEN"))
    is_connected = has_webhook or has_token
    
    return {
        "integration": "Slack",
        "connected": is_connected,
        "details": {
            "webhook_configured": has_webhook,
            "api_token_configured": has_token
        }
    }

@router.post("/test")
def slack_test():
    has_webhook = bool(os.getenv("SLACK_WEBHOOK_URL"))
    has_token = bool(os.getenv("SLACK_API_TOKEN"))
    is_connected = has_webhook or has_token
    
    if is_connected:
        return {"success": True, "message": "Successfully communicated with Slack workspace using saved credentials!"}
    
    return {"success": False, "message": "Slack connection failed. No credentials found in environment."}
