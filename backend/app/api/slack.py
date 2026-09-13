from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def slack_status():
    return {"message": "Slack API is reachable."}
