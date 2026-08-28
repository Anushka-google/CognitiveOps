from fastapi import APIRouter

from app.models.intent import IntentRequest
from app.services.intent_service import detect_intent


router = APIRouter()


@router.post("/intent")
async def classify_intent(
	request: IntentRequest
):
	return detect_intent(
		request.question
	)
