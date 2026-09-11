from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.intent_service import (
    IntentService
)

from app.services.retrieval_service import (
    RetrievalService
)

from app.services.llm_service import (
    generate_answer
)

from app.services.jira_service import (
    JiraService
)


router = APIRouter()


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    question: str


# =========================================================
# HELPERS
# =========================================================

def _build_jira_context(workflows):
    if not workflows:
        return ""

    lines = []

    for workflow in workflows:

        if isinstance(workflow, dict):

            lines.append(
                " | ".join(
                    f"{key}: {value}"
                    for key, value in workflow.items()
                )
            )

        else:
            lines.append(
                str(workflow)
            )

    return "\n".join(lines)


def _build_rag_context(retrieval_result):
    results = retrieval_result.get(
        "results",
        []
    )

    if not results:
        return ""

    context_parts = []

    for index, item in enumerate(
        results,
        start=1
    ):

        document = item.get(
            "document",
            ""
        )

        metadata = item.get(
            "metadata",
            {}
        )

        context_parts.append(
            f"""
Evidence {index}:
{document}

Metadata:
{metadata}
""".strip()
        )

    return "\n\n".join(
        context_parts
    )


def _build_citations(
    retrieval_result
):

    citations = []

    for item in retrieval_result.get(
        "results",
        []
    ):

        metadata = item.get(
            "metadata",
            {}
        )

        issue_id = metadata.get(
            "issue_id"
        )

        source = metadata.get(
            "source"
        )

        source_type = metadata.get(
            "source_type"
        )

        if issue_id:

            citations.append(
                {
                    "type": "issue",
                    "source": source or "workflow",
                    "issue_id": issue_id
                }
            )

        elif source:

            citations.append(
                {
                    "type": "source",
                    "source": source,
                    "source_type": source_type
                }
            )

    return citations


# =========================================================
# CHAT ENDPOINT
# =========================================================

@router.post(
    "/chat"
)
async def chat(
    request: ChatRequest
):

    question = (
        request.question.strip()
    )

    if not question:

        return {
            "question": "",
            "intent": "unknown",
            "confidence": 0.0,
            "answer": (
                "Please provide a question."
            ),
            "evidence": [],
            "citations": [],
            "insufficient_evidence": True
        }

    # =====================================================
    # 1. INTENT
    # =====================================================

    intent_result = (
        IntentService().detect(
            question
        )
    )

    # =====================================================
    # 2. RAG RETRIEVAL
    # =====================================================

    retrieval_result = (
        RetrievalService().retrieve(
            query=question,
            n_results=5,
            distance_threshold=1.5,
            min_evidence=1
        )
    )

    rag_context = (
        _build_rag_context(
            retrieval_result
        )
    )

    # =====================================================
    # 3. JIRA EVIDENCE
    # =====================================================

    jira_context = ""

    try:

        jira_service = (
            JiraService()
        )

        workflows = (
            jira_service
            .get_workflow_records()
        )

        jira_context = (
            _build_jira_context(
                workflows
            )
        )

    except Exception:

        jira_context = ""

    # =====================================================
    # 4. COMBINE EVIDENCE
    # =====================================================

    context_parts = []

    if rag_context:

        context_parts.append(
            "RAG EVIDENCE:\n"
            + rag_context
        )

    if jira_context:

        context_parts.append(
            "JIRA WORKFLOW EVIDENCE:\n"
            + jira_context
        )

    context = "\n\n".join(
        context_parts
    )

    # =====================================================
    # 5. EVIDENCE GUARDRAIL
    # =====================================================

    if not context.strip():

        return {
            "question": question,
            "intent": intent_result.intent.value,
            "confidence": (
                intent_result.confidence
            ),
            "answer": (
                "I don't have enough "
                "evidence to answer this "
                "reliably."
            ),
            "evidence": [],
            "citations": [],
            "insufficient_evidence": True
        }

    # =====================================================
    # 6. GROUNDED ANSWER
    # =====================================================
    try:
        answer = generate_answer(
        question=question,
        context=context
    )

    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                "Gemini API quota exceeded. "
                "Chat is temporarily unavailable. "
                "Please wait for the Gemini quota "
                "to reset and try again."
            )
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate the chat response."
    )

    # =====================================================
    # 7. CITATIONS
    # =====================================================

    citations = _build_citations(
        retrieval_result
    )

    # =====================================================
    # 8. RESPONSE
    # =====================================================

    return {
        "question": question,

        "intent": (
            intent_result.intent.value
        ),

        "confidence": (
            intent_result.confidence
        ),

        "reasoning": (
            intent_result.reasoning
        ),

        "answer": answer,

        "evidence": (
            retrieval_result.get(
                "results",
                []
            )
        ),

        "citations": citations,

        "insufficient_evidence": (
            retrieval_result.get(
                "status"
            )
            in {
                "no_evidence",
                "insufficient_evidence"
            }
        ),

        "conflict_detected": (
            retrieval_result.get(
                "conflict_detected",
                False
            )
        )
    }