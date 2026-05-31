from fastapi import APIRouter

from app.models.query import QueryRequest
from app.services.vector_store import get_context
from app.services.llm_service import generate_answer

router = APIRouter()


@router.post("/query")
async def query_rag(
    request: QueryRequest
):
    context = get_context(
        request.question
    )

    answer = generate_answer(
        question=request.question,
        context=context
    )

    return {
        "question": request.question,
        "context": context,
        "answer": answer
    }