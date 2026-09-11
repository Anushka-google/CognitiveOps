import logging
import time

from app.agents.state import AgentState

from app.models.insight import Insight

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


# =========================================================
# Agent Output Helpers
# =========================================================

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


# =========================================================
# SLA Decision Builder
# =========================================================

def _build_sla_decision(
    sla_prediction: dict,
    sla_features: dict | None = None,
) -> dict:

    sla_prediction = (
        sla_prediction
        if isinstance(
            sla_prediction,
            dict
        )
        else {}
    )

    sla_features = (
        sla_features
        if isinstance(
            sla_features,
            dict
        )
        else {}
    )

    probability = sla_prediction.get(
        "sla_breach_probability"
    )

    risk_level = sla_prediction.get(
        "risk_level",
        "Unknown"
    )

    if probability is None:

        return {

            "risk_level": risk_level,

            "contributing_factors": [],

            "explanation": (
                "SLA breach probability is "
                "currently unavailable."
            ),

            "recommendation": (
                "Additional SLA prediction data "
                "is required before taking "
                "SLA-related action."
            )
        }

    try:

        probability = float(
            probability
        )

    except (
        TypeError,
        ValueError
    ):

        probability = None

    if probability is None:

        return {

            "risk_level": risk_level,

            "contributing_factors": [],

            "explanation": (
                "The SLA prediction returned "
                "an invalid probability."
            ),

            "recommendation": (
                "Validate the SLA model output "
                "before taking action."
            )
        }

    probability = max(
        0.0,
        min(
            1.0,
            probability
        )
    )

    def numeric(
        name: str
    ) -> float:

        try:

            return float(
                sla_features.get(
                    name,
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0

    backlog_age_hours = numeric(
        "backlog_age_hours"
    )

    waiting_ratio = numeric(
        "waiting_ratio"
    )

    blocker_density = numeric(
        "blocker_density"
    )

    reassignment_rate = numeric(
        "reassignment_rate"
    )

    dependency_count = numeric(
        "dependency_count"
    )

    workflow_complexity = numeric(
        "workflow_complexity"
    )

    agent_queue_length = numeric(
        "agent_queue_length_at_submit"
    )

    response_time_hours = numeric(
        "response_time_hours"
    )

    factors = []

    if backlog_age_hours >= 72:

        factors.append(
            f"Long backlog age "
            f"({backlog_age_hours:.1f} hours)."
        )

    elif backlog_age_hours >= 24:

        factors.append(
            f"Extended waiting time "
            f"({backlog_age_hours:.1f} hours)."
        )

    if waiting_ratio >= 0.80:

        factors.append(
            f"High waiting ratio "
            f"({waiting_ratio:.2f})."
        )

    elif waiting_ratio >= 0.60:

        factors.append(
            f"Elevated waiting ratio "
            f"({waiting_ratio:.2f})."
        )

    if blocker_density > 0:

        factors.append(
            f"Workflow blocker density "
            f"is {blocker_density:.2f}."
        )

    if reassignment_rate > 0:

        factors.append(
            f"Reassignment activity detected "
            f"({reassignment_rate:.2f})."
        )

    if dependency_count > 0:

        factors.append(
            f"Workflow has "
            f"{dependency_count:.0f} dependencies."
        )

    if workflow_complexity >= 3:

        factors.append(
            f"Elevated workflow complexity "
            f"({workflow_complexity:.2f})."
        )

    if agent_queue_length >= 3:

        factors.append(
            f"Assigned agent has "
            f"{agent_queue_length:.0f} other "
            f"active workflow items."
        )

    if response_time_hours >= 24:

        factors.append(
            f"Response time is high "
            f"({response_time_hours:.1f} hours)."
        )

    if not factors:

        factors.append(
            "The predictive model identified "
            "workflow characteristics associated "
            "with SLA breach risk."
        )

    explanation = (
        f"The TensorFlow model predicts a "
        f"{probability * 100:.1f}% probability "
        f"of SLA breach, classified as "
        f"{risk_level} risk."
    )

    if risk_level == "High":

        recommendation = (
            "Prioritize this workflow immediately. "
            "Review the contributing factors, "
            "resolve blockers or dependencies, "
            "and consider escalation before the "
            "SLA is breached."
        )

    elif risk_level == "Medium":

        recommendation = (
            "Monitor this workflow closely and "
            "address the identified contributing "
            "factors before the SLA risk increases."
        )

    elif risk_level == "Low":

        recommendation = (
            "Continue normal workflow monitoring. "
            "No immediate SLA intervention is "
            "required."
        )

    else:

        recommendation = (
            "Review the available workflow and "
            "prediction data before taking "
            "SLA-related action."
        )

    return {

        "risk_level": risk_level,

        "contributing_factors": factors,

        "explanation": explanation,

        "recommendation": recommendation
    }


# =========================================================
# Reasoning Agent
# =========================================================

def reasoning_agent(
    state: AgentState
):

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

    evidence_safety_status = (
        "not_evaluated"
    )

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

    sla_prediction = state.get(
        "sla_prediction",
        {}
    )

    sla_features = state.get(
        "sla_features",
        {}
    )

    # =========================================================
    # NEW: ROOT CAUSE GRAPH
    # =========================================================

    root_cause_graph = state.get(
        "root_cause_graph",
        {}
    )

    if not isinstance(
        root_cause_graph,
        dict
    ):

        root_cause_graph = {}

    graph_nodes = root_cause_graph.get(
        "nodes",
        []
    )

    graph_edges = root_cause_graph.get(
        "edges",
        []
    )

    if not isinstance(
        graph_nodes,
        list
    ):

        graph_nodes = []

    if not isinstance(
        graph_edges,
        list
    ):

        graph_edges = []

    logger.info(
        "ROOT CAUSE GRAPH | "
        "nodes=%s | edges=%s",
        len(graph_nodes),
        len(graph_edges)
    )

    trace_log(
        "ROOT_CAUSE_GRAPH_RECEIVED",
        (
            f"nodes={len(graph_nodes)} "
            f"edges={len(graph_edges)}"
        )
    )

    # =========================================================
    # SAFETY NORMALIZATION
    # =========================================================

    if not isinstance(
        sla_prediction,
        dict
    ):

        sla_prediction = {}

    if not isinstance(
        sla_features,
        dict
    ):

        sla_features = {}

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

    # =========================================================
    # NEW: PASS GRAPH INTO COMBINED EVIDENCE
    # =========================================================

    combined_evidence[
        "root_cause_graph"
    ] = root_cause_graph

    logger.info(
        "REASONING EVIDENCE | "
        "jira=%s | slack=%s | "
        "graph_nodes=%s | graph_edges=%s",
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
        ),
        len(graph_nodes),
        len(graph_edges)
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

    # =========================================================
    # 4. BUILD SLA DECISION
    # =========================================================

    sla_decision = _build_sla_decision(
        sla_prediction,
        sla_features
    )

    # =========================================================
    # 5. START WITH EXISTING INSIGHTS
    # =========================================================

    reasoning_inputs = list(
        existing_insights
    )

    # =========================================================
    # 6. CREATE EVIDENCE-BASED INSIGHTS IF NEEDED
    # =========================================================

    if not reasoning_inputs:

        for jira_item in jira_evidence:

            if not isinstance(
                jira_item,
                dict
            ):

                continue

            issue_key = (
                jira_item.get(
                    "ticket_id"
                )
                or jira_item.get(
                    "issue_key"
                )
                or jira_item.get(
                    "key"
                )
            )

            title = (
                jira_item.get(
                    "title"
                )
                or jira_item.get(
                    "summary"
                )
                or "Jira workflow issue"
            )

            severity = (
                jira_item.get(
                    "risk_level"
                )
                or jira_item.get(
                    "severity"
                )
                or jira_item.get(
                    "priority"
                )
                or "Medium"
            )

            days_waiting = jira_item.get(
                "days_waiting"
            )

            issue_text = (
                f"{issue_key}: {title}"
                if issue_key
                else title
            )

            impact_text = (
                "The workflow may be affected "
                "by the observed Jira conditions."
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

                evidence_insight = (
                    Insight(
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

            except Exception as e:

                logger.warning(
                    "UNABLE TO CREATE WORKFLOW INSIGHT | "
                    "ticket=%s | error=%s",
                    issue_key,
                    e
                )

                continue

    # =========================================================
    # 7. NOTHING TO REASON ABOUT
    # =========================================================

    if not reasoning_inputs:

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

                "root_cause_graph_nodes": (
                    len(graph_nodes)
                ),

                "root_cause_graph_edges": (
                    len(graph_edges)
                ),

                "evidence_evaluations": (
                    evidence_evaluations
                ),

                "evidence_safety_status": (
                    evidence_safety_status
                ),

                "sla_prediction": (
                    sla_prediction
                ),

                "sla_decision": (
                    sla_decision
                )
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        return {

            "insights": [],

            "combined_evidence": (
                combined_evidence
            ),

            "agent_outputs": (
                agent_outputs
            ),

            "sla_prediction": (
                sla_prediction
            ),

            "sla_features": (
                sla_features
            ),

            "sla_decision": (
                sla_decision
            ),

            "root_cause_graph": (
                root_cause_graph
            ),

            "reasoning_completed": True
        }

    # =========================================================
    # 8. INITIALIZE GEMINI
    # =========================================================

    try:

        gemini_service = (
            GeminiInsightService()
        )

    except Exception as e:

        logger.exception(
            "GEMINI SERVICE INIT FAILED | %s",
            e
        )

        gemini_service = None

    # =========================================================
    # 9. BUILD REASONING CONTEXT
    # =========================================================

    analysis_context = {

        **combined_evidence,

        "long_term_memory": (
            long_term_memory
        ),

        "sla_prediction": (
            sla_prediction
        ),

        "sla_features": (
            sla_features
        ),

        "sla_decision": (
            sla_decision
        ),

        # Explicit graph field
        "root_cause_graph": (
            root_cause_graph
        )
    }

    logger.info(
        "REASONING CONTEXT | "
        "jira=%s | slack=%s | memory=%s | "
        "graph_nodes=%s | graph_edges=%s",
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
        ),
        len(graph_nodes),
        len(graph_edges)
    )

    # =========================================================
    # 10. GEMINI REASONING + EVIDENCE SAFETY GATE
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

                    evaluation = {

                        **evaluation,

                        "sufficient": False,

                        "guardrail_status": (
                            "blocked"
                        ),

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

                if not evaluation.get(
                    "sufficient",
                    False
                ):

                    evidence_safety_status = (
                        "blocked_insufficient_evidence"
                    )

                    if hasattr(
                        insight,
                        "impact"
                    ):

                        insight.impact = (
                            "Impact cannot be reliably "
                            "determined from the available "
                            "evidence."
                        )

                    if hasattr(
                        insight,
                        "recommendation"
                    ):

                        insight.recommendation = (
                            "Additional evidence is required "
                            "before generating a reliable "
                            "recommendation."
                        )

                    updated_insight = (
                        insight
                    )

                    updated_insights.append(
                        updated_insight
                    )

                    continue

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
        # 11. FINAL METRICS
        # =========================================================

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

                "root_cause_graph_nodes": (
                    len(graph_nodes)
                ),

                "root_cause_graph_edges": (
                    len(graph_edges)
                ),

                "evidence_evaluations": (
                    evidence_evaluations
                ),

                "evidence_safety_status": (
                    evidence_safety_status
                ),

                "sla_prediction": (
                    sla_prediction
                ),

                "sla_decision": (
                    sla_decision
                )
            },

            "execution_time": (
                execution_time
            ),

            "error": None
        }

        return {

            "insights": (
                updated_insights
            ),

            "combined_evidence": (
                combined_evidence
            ),

            "agent_outputs": (
                agent_outputs
            ),

            "sla_prediction": (
                sla_prediction
            ),

            "sla_features": (
                sla_features
            ),

            "sla_decision": (
                sla_decision
            ),

            # Keep graph available downstream
            "root_cause_graph": (
                root_cause_graph
            ),

            "reasoning_completed": True
        }

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

        agent_outputs = _copy_agent_outputs(
            state
        )

        agent_outputs[
            "reasoning_agent"
        ] = {

            "agent": "reasoning_agent",

            "status": "failed",

            "output": {

                "root_cause_graph_nodes": (
                    len(graph_nodes)
                ),

                "root_cause_graph_edges": (
                    len(graph_edges)
                ),

                "evidence_evaluations": (
                    evidence_evaluations
                ),

                "evidence_safety_status": (
                    evidence_safety_status
                ),

                "sla_prediction": (
                    sla_prediction
                ),

                "sla_decision": (
                    sla_decision
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

            "sla_prediction": (
                sla_prediction
            ),

            "sla_features": (
                sla_features
            ),

            "sla_decision": (
                sla_decision
            ),

            "root_cause_graph": (
                root_cause_graph
            ),

            "reasoning_completed": False,

            "errors": [
                str(e)
            ]
        }