from enum import Enum

from pydantic import BaseModel



class IntentRequest(BaseModel):

    question: str


class IntentType(str, Enum):

    ANALYZE_WORKFLOW = "analyze_workflow"

    FIND_BOTTLENECK = "find_bottleneck"

    EXPLAIN_DELAY = "explain_delay"

    RECOMMEND_ACTION = "recommend_action"

    RETRIEVE_JIRA_ISSUE = "retrieve_jira_issue"

    UNKNOWN = "unknown"


class IntentResult(BaseModel):

    intent: IntentType

    confidence: float

    reasoning: str | None = None