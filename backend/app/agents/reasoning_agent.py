import logging
import time

from app.agents.state import AgentState

from app.services.gemini_insight_service import (
    GeminiInsightService
)

from app.services.recommendation_service import (
    RecommendationService
)

from app.services.trace_service import (
    set_agent_name,
    trace_log
)


logger = logging.getLogger(__name__)


# =========================================================
# Evidence Evaluation Guardrail
# =========================================================

def _validate_evidence_evaluation(
    evaluation: dict
) -> tuple[bool, str]:

    if not isinstance(
        evaluation,
        dict
    ):

        return (
            False,
            "Evidence evaluation is not a dictionary."
        )

    if not isinstance(
        evaluation.get("sufficient"),
        bool
    ):

        return (
            False,
            "Evidence sufficiency is invalid."
        )

    required_scores = (
        "relevance",
        "specificity",
        "support",
        "completeness"
    )

    for field in required_scores:

        try:

            score = float(
                evaluation.get(field)
            )

        except (
            TypeError,
            ValueError
        ):

            return (
                False,
                f"Invalid evidence score: {field}"
            )

        if not 0.0 <= score <= 1.0:

            return (
                False,
                f"Evidence score out of range: {field}"
            )

    if not isinstance(
        evaluation.get("reason"),
        str
    ):

        return (
            False,
            "Evidence evaluation reason is invalid."
        )

    if not evaluation.get(
        "reason"
    ).strip():

        return (
            False,
            "Evidence evaluation reason is empty."
        )

    if not isinstance(
        evaluation.get(
            "missing_information"
        ),
        list
    ):

        return (
            False,
            "Missing information must be a list."
        )

    return (
        True,
        "Evidence evaluation is valid."
    )


def _copy_agent_outputs(
    state: AgentState
):

    return dict(
        state.get(
            "agent_outputs",
            {}
        )
    )


def _copy_errors(
    state: AgentState
):

    return list(
        state.get(
            "errors",
            []
        )
    )


def reasoning_agent(
    state: AgentState
):

    # =========================================================
    # TRACE CONTEXT
    # =========================================================

    set_agent_name(
        "reasoning_agent"
    )

    trace_log(
        "AGENT_START"
    )

    logger.info(
        "AGENT START | reasoning_agent"
    )

    start_time = time.perf_counter()

    updated_insights = []

    gemini_used = False

    evidence_evaluations = []

    evidence_safety_status = "not_evaluated"

    # =========================================================
    # 1. READ EVIDENCE FROM STATE
    # =========================================================

    jira_evidence = state.get(
        "jira_evidence",
        []
    )

    slack_evidence = state.get(
        "slack_evidence",
        []
    )

    combined_evidence = state.get(
        "combined_evidence",
        {}
    )

    existing_insights = state.get(
        "insights",
        []
    )

    if not isinstance(
        jira_evidence,
        list
    ):

        jira_evidence = []

    if not isinstance(
        slack_evidence,
        list
    ):

        slack_evidence = []

    if not isinstance(
        existing_insights,
        list
    ):

        existing_insights = []

    if not isinstance(
        combined_evidence,
        dict
    ):

        combined_evidence = {}

    logger.info(
        "REASONING INPUT | "
        "jira=%s | slack=%s | insights=%s",
        len(jira_evidence),
        len(slack_evidence),
        len(existing_insights)
    )

    trace_log(
        "REASONING_INPUT",
        (
            f"jira={len(jira_evidence)} "
            f"slack={len(slack_evidence)} "
            f"insights={len(existing_insights)}"
        )
    )

    # =========================================================
    # 2. BUILD RELIABLE COMBINED EVIDENCE
    # =========================================================

    if not combined_evidence.get(
        "jira"
    ):

        combined_evidence[
            "jira"
        ] = jira_evidence

    if not combined_evidence.get(
        "slack"
    ):

        combined_evidence[
            "slack"
        ] = slack_evidence

    logger.info(
        "REASONING EVIDENCE | "
        "jira=%s | slack=%s",
        len(
            combined_evidence.get(
                "jira",
                []
            )
        ),
        len(
            combined_evidence.get(
                "slack",
                []
            )
        )
    )

    # =========================================================
    # 3. LONG-TERM MEMORY
    # =========================================================

    long_term_memory = state.get(
        "long_term_memory",
        []
    )

    if not isinstance(
        long_term_memory,
        list
    ):

        long_term_memory = []

    logger.info(
        "LONG-TERM MEMORY | "
        "reasoning_agent | count=%s",
        len(long_term_memory)
    )

    # =========================================================
    # 4. START WITH EXISTING PATTERN INSIGHTS
    # =========================================================

    reasoning_inputs = list(
        existing_insights
    )

    # =========================================================
    # 5. FALLBACK:
    #    CREATE INSIGHTS FROM JIRA EVIDENCE
    # =========================================================

    if not reasoning_inputs:

        logger.warning(
            "NO PATTERN INSIGHTS | "
            "attempting evidence-based insight generation"
        )

        for item in jira_evidence:

            if not isinstance(
                item,
                dict
            ):

                continue

            issue_key = (
                item.get("key")
                or item.get("issue_key")
                or item.get("ticket")
                or item.get("id")
            )

            if not issue_key:

                logger.warning(
                    "JIRA EVIDENCE WITHOUT ISSUE KEY"
                )

                continue

            summary = (
                item.get("summary")
                or item.get("title")
                or item.get("description")
                or "Jira operational issue"
            )

            status = (
                item.get("status")
                or item.get("issue_status")
                or item.get("state")
                or "Unknown"
            )

            priority = (
                item.get("priority")
                or item.get("priority_name")
                or "Unknown"
            )

            days_waiting = item.get(
                "days_waiting"
            )

            priority_text = str(
                priority
            ).strip().lower()

            severity = "Low"

            if priority_text in {
                "highest",
                "critical",
                "blocker"
            }:

                severity = "High"

            elif priority_text in {
                "high",
                "major"
            }:

                severity = "High"

            elif priority_text in {
                "medium",
                "normal"
            }:

                severity = "Medium"

            if isinstance(
                days_waiting,
                (int, float)
            ):

                if days_waiting >= 7:

                    severity = "High"

                elif days_waiting >= 3:

                    if severity == "Low":

                        severity = "Medium"

            issue_text = (
                f"{issue_key}: {summary}"
            )

            impact_text = (
                f"Ticket {issue_key} is currently "
                f"{status} with priority {priority}."
            )

            if isinstance(
                days_waiting,
                (int, float)
            ):

                impact_text += (
                    f" The ticket has been waiting "
                    f"for approximately "
                    f"{days_waiting} days."
                )

            recommendation_text = (
                f"Review Jira ticket {issue_key} "
                f"and determine whether escalation, "
                f"reassignment, or priority adjustment "
                f"is required."
            )

            try:

                from app.services.workflow_analyzer import (
                    WorkflowInsight
                )

                evidence_insight = (
                    WorkflowInsight(
                        issue=issue_text,

                        severity=severity,

                        impact=impact_text,

                        recommendation=(
                            recommendation_text
                        )
                    )
                )

                reasoning_inputs.append(
                    evidence_insight
                )

                logger.info(
                    "EVIDENCE INSIGHT CREATED | "
                    "ticket=%s | severity=%s",
                    issue_key,
                    severity
                )

            except Exception as e:

                logger.warning(
                    "UNABLE TO CREATE WORKFLOW INSIGHT | "
                    "ticket=%s | error=%s",
                    issue_key,
                    e
                )

                continue

        logger.info(
            "EVIDENCE-BASED INSIGHTS CREATED | "
            "count=%s",
            len(reasoning_inputs)
        )

    # =========================================================
    # 6. NOTHING TO REASON ABOUT
    # =========================================================

    if not reasoning_inputs:

        logger.warning(
            "REASONING STOPPED | "
            "no insights and no usable Jira evidence"
        )

        trace_log(
            "REASONING_STOPPED",
            "reason=no_reasoning_inputs"
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        agent_outputs = _copy_agent_outputs(
            state
        )

        agent_outputs[
            "reasoning_agent"
        ] = {

            "agent": "reasoning_agent",

            "status": "success",

            "output": {

                "insights_count": 0,

                "gemini_used": False,

                "jira_evidence_count": (
                    len(jira_evidence)
                ),

                "slack_evidence_count": (
                    len(slack_evidence)
                ),

                "evidence_evaluations": (
                    evidence_evaluations
                ),

                "evidence_safety_status": (
                    evidence_safety_status
                ),

                "reason": (
                    "No usable insights or evidence "
                    "were available for reasoning."
                )
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        logger.info(
            "AGENT END | reasoning_agent | "
            "no reasoning inputs"
        )

        trace_log(
            "AGENT_END",
            (
                f"execution_time={execution_time:.2f}s "
                "status=no_reasoning_inputs"
            )
        )

        return {

            "insights": [],

            "combined_evidence": (
                combined_evidence
            ),

            "agent_outputs": (
                agent_outputs
            )
        }

    # =========================================================
    # 7. INITIALIZE GEMINI ONLY WHEN REQUIRED
    # =========================================================

    try:

        gemini_service = (
            GeminiInsightService()
        )

        trace_log(
            "GEMINI_SERVICE_READY"
        )

    except Exception as e:

        logger.exception(
            "GEMINI SERVICE INIT FAILED | %s",
            e
        )

        trace_log(
            "GEMINI_SERVICE_FAILED",
            str(e),
            logging.ERROR
        )

        gemini_service = None

    # =========================================================
    # 8. BUILD REASONING CONTEXT
    # =========================================================

    analysis_context = {

        **combined_evidence,

        "long_term_memory": (
            long_term_memory
        )
    }

    logger.info(
        "REASONING CONTEXT | "
        "jira=%s | slack=%s | memory=%s",
        len(
            analysis_context.get(
                "jira",
                []
            )
        ),
        len(
            analysis_context.get(
                "slack",
                []
            )
        ),
        len(
            analysis_context.get(
                "long_term_memory",
                []
            )
        )
    )

    # =========================================================
    # 9. GEMINI REASONING + EVIDENCE SAFETY GATE
    # =========================================================

    try:

        for insight in reasoning_inputs:

            updated_insight = insight

            try:

                if gemini_service is None:

                    raise RuntimeError(
                        "GeminiInsightService "
                        "is unavailable."
                    )

                # =================================================
                # 9A. EVIDENCE EVALUATION
                # =================================================

                trace_log(
                    "EVIDENCE_EVALUATION_START"
                )

                evaluation = (
                    gemini_service
                    .evaluate_evidence(
                        insight,
                        analysis_context
                    )
                )

                if not isinstance(
                    evaluation,
                    dict
                ):

                    evaluation = {
                        "sufficient": False,
                        "relevance": 0.0,
                        "specificity": 0.0,
                        "support": 0.0,
                        "completeness": 0.0,
                        "reason": (
                            "Invalid evidence "
                            "evaluation returned."
                        ),
                        "missing_information": []
                    }

                evaluation_valid, validation_reason = (
                    _validate_evidence_evaluation(
                        evaluation
                    )
                )

                if not evaluation_valid:

                    evidence_safety_status = (
                        "blocked_invalid_evaluation"
                    )

                    logger.warning(
                        "EVIDENCE GUARDRAIL BLOCKED | "
                        "reason=%s",
                        validation_reason
                    )

                    trace_log(
                        "EVIDENCE_GUARDRAIL_BLOCKED",
                        (
                            f"reason={validation_reason}"
                        ),
                        logging.WARNING
                    )

                    evaluation = {
                        **evaluation,
                        "sufficient": False,
                        "guardrail_status": "blocked",
                        "guardrail_reason": (
                            validation_reason
                        )
                    }

                else:

                    evidence_safety_status = (
                        "evaluation_valid"
                    )

                evidence_evaluations.append(
                    evaluation
                )

                logger.info(
                    "EVIDENCE EVALUATION | "
                    "sufficient=%s | "
                    "relevance=%.2f | "
                    "specificity=%.2f | "
                    "support=%.2f | "
                    "completeness=%.2f",
                    evaluation.get(
                        "sufficient",
                        False
                    ),
                    float(
                        evaluation.get(
                            "relevance",
                            0.0
                        )
                    ),
                    float(
                        evaluation.get(
                            "specificity",
                            0.0
                        )
                    ),
                    float(
                        evaluation.get(
                            "support",
                            0.0
                        )
                    ),
                    float(
                        evaluation.get(
                            "completeness",
                            0.0
                        )
                    )
                )

                # =================================================
                # 9B. HARD EVIDENCE SAFETY GATE
                # =================================================

                if not evaluation.get(
                    "sufficient",
                    False
                ):

                    evidence_safety_status = (
                        "blocked_insufficient_evidence"
                    )

                    logger.warning(
                        "EVIDENCE INSUFFICIENT | "
                        "Gemini insight generation skipped | "
                        "fallback recommendation blocked"
                    )

                    trace_log(
                        "EVIDENCE_REASONING_BLOCKED",
                        (
                            "reason=insufficient_evidence"
                        ),
                        logging.WARNING
                    )

                    if hasattr(
                        insight,
                        "impact"
                    ):

                        insight.impact = (
                            "Impact cannot be reliably "
                            "determined from the available evidence."
                        )

                    if hasattr(
                        insight,
                        "recommendation"
                    ):

                        insight.recommendation = (
                            "Additional evidence is required "
                            "before generating a reliable recommendation."
                        )

                    updated_insight = (
                        insight
                    )

                    updated_insights.append(
                        updated_insight
                    )

                    continue

                # =================================================
                # 9C. SUFFICIENT EVIDENCE
                #     → ALLOW GEMINI REASONING
                # =================================================

                evidence_safety_status = (
                    "approved_for_reasoning"
                )

                trace_log(
                    "INSIGHT_GENERATION_START"
                )

                updated_insight = (
                    gemini_service
                    .generate_insight_analysis(
                        insight,
                        analysis_context,
                        long_term_memory
                    )
                )

                gemini_used = True

                trace_log(
                    "INSIGHT_GENERATION_SUCCESS"
                )

                logger.info(
                    "GEMINI REASONING SUCCESS"
                )

            except Exception as e:

                logger.error(
                    "GEMINI ERROR | "
                    "reasoning_agent | %s",
                    e
                )

                trace_log(
                    "REASONING_OPERATION_FAILED",
                    str(e),
                    logging.ERROR
                )

                evidence_safety_status = (
                    "blocked_reasoning_error"
                )

                logger.warning(
                    "REASONING GUARDRAIL | "
                    "fallback recommendation blocked | "
                    "reason=%s",
                    e
                )

                if hasattr(
                    insight,
                    "impact"
                ):

                    insight.impact = (
                        "Impact cannot be reliably "
                        "determined because reasoning "
                        "validation failed."
                    )

                if hasattr(
                    insight,
                    "recommendation"
                ):

                    insight.recommendation = (
                        "Additional validation is required "
                        "before generating a recommendation."
                    )

                updated_insight = (
                    insight
                )

            updated_insights.append(
                updated_insight
            )

        # =========================================================
        # 10. FINAL EXECUTION METRICS
        # =========================================================

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AGENT END | reasoning_agent | "
            "execution_time=%.2fs | "
            "insights=%s | "
            "gemini_used=%s | "
            "evidence_safety=%s",
            execution_time,
            len(updated_insights),
            gemini_used,
            evidence_safety_status
        )

        trace_log(
            "AGENT_END",
            (
                f"execution_time={execution_time:.2f}s "
                f"insights={len(updated_insights)} "
                f"gemini_used={gemini_used} "
                f"evidence_safety={evidence_safety_status}"
            )
        )

        # =========================================================
        # 11. STRUCTURED AGENT OUTPUT
        # =========================================================

        agent_outputs = _copy_agent_outputs(
            state
        )

        agent_outputs[
            "reasoning_agent"
        ] = {

            "agent": "reasoning_agent",

            "status": "success",

            "output": {

                "insights_count": (
                    len(updated_insights)
                ),

                "gemini_used": (
                    gemini_used
                ),

                "jira_evidence_count": (
                    len(
                        combined_evidence.get(
                            "jira",
                            []
                        )
                    )
                ),

                "slack_evidence_count": (
                    len(
                        combined_evidence.get(
                            "slack",
                            []
                        )
                    )
                ),

                "evidence_evaluations": (
                    evidence_evaluations
                ),

                "evidence_safety_status": (
                    evidence_safety_status
                )
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        logger.info(
            "STRUCTURED OUTPUT | "
            "agent=reasoning_agent | "
            "status=success"
        )

        return {

            "insights": (
                updated_insights
            ),

            "combined_evidence": (
                combined_evidence
            ),

            "agent_outputs": (
                agent_outputs
            )
        }

    # =========================================================
    # 12. COMPLETE AGENT FAILURE
    # =========================================================

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "AGENT FAILED | reasoning_agent | "
            "execution_time=%.2fs",
            execution_time
        )

        trace_log(
            "AGENT_FAILED",
            (
                f"execution_time={execution_time:.2f}s "
                f"error={e}"
            ),
            logging.ERROR
        )

        agent_outputs = _copy_agent_outputs(
            state
        )

        agent_outputs[
            "reasoning_agent"
        ] = {

            "agent": "reasoning_agent",

            "status": "failed",

            "output": {

                "evidence_evaluations": (
                    evidence_evaluations
                ),

                "evidence_safety_status": (
                    evidence_safety_status
                )
            },

            "execution_time": (
                execution_time
            ),

            "error": str(e)
        }

        return {

            "agent_outputs": (
                agent_outputs
            ),

            "errors": [
                str(e)
            ]
        }