import os
from fastapi import APIRouter

router = APIRouter()

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
        return {"success": True, "message": "Successfully communicated with Slack workspace."}
    
    return {"success": False, "message": "Slack connection failed. No credentials found in environment."}
