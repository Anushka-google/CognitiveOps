from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def reports_status():
    return {"message": "Reports API is reachable."}
