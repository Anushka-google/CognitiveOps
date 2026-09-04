import logging
import time

from app.agents.state import AgentState

from app.services.gemini_insight_service import (
    GeminiInsightService
)

from app.services.recommendation_service import (
    RecommendationService
)


logger = logging.getLogger(__name__)


def reasoning_agent(
    state: AgentState
):

    logger.info(
        "AGENT START | reasoning_agent"
    )

    start_time = time.perf_counter()

    updated_insights = []

    gemini_used = False

    # =========================================================
    # 1. INITIALIZE SERVICES
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

    try:

        recommendation_service = (
            RecommendationService()
        )

    except Exception as e:

        logger.exception(
            "RECOMMENDATION SERVICE INIT FAILED | %s",
            e
        )

        recommendation_service = None

    # =========================================================
    # 2. READ EVIDENCE FROM STATE
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

    # Safety checks
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

    # =========================================================
    # 3. BUILD RELIABLE COMBINED EVIDENCE
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
    # 4. LONG-TERM MEMORY
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
    # 5. START WITH EXISTING PATTERN INSIGHTS
    # =========================================================

    reasoning_inputs = list(
        existing_insights
    )

    # =========================================================
    # 6. FALLBACK:
    #    CREATE INSIGHTS FROM JIRA EVIDENCE
    #
    # Problem:
    #
    # PatternAgent can return:
    #
    #     insights = []
    #
    # even when Jira evidence exists.
    #
    # Previously reasoning_agent then had nothing to reason
    # about.
    #
    # Now Jira evidence can become a valid WorkflowInsight.
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

            # -------------------------------------------------
            # Extract ticket identity
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Extract ticket information
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Normalize priority
            # -------------------------------------------------

            priority_text = str(
                priority
            ).strip().lower()

            # -------------------------------------------------
            # Determine severity
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Waiting-time based escalation
            # -------------------------------------------------

            if isinstance(
                days_waiting,
                (int, float)
            ):

                if days_waiting >= 7:

                    severity = "High"

                elif days_waiting >= 3:

                    if severity == "Low":

                        severity = "Medium"

            # -------------------------------------------------
            # Build operational issue text
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Construct project's WorkflowInsight object
            # -------------------------------------------------

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
    # 7. NOTHING TO REASON ABOUT
    # =========================================================

    if not reasoning_inputs:

        logger.warning(
            "REASONING STOPPED | "
            "no insights and no usable Jira evidence"
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
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
    # 9. GEMINI REASONING
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

                updated_insight = (
                    gemini_service
                    .generate_insight_analysis(
                        insight,
                        analysis_context
                    )
                )

                gemini_used = True

                logger.info(
                    "GEMINI REASONING SUCCESS"
                )

            except Exception as e:

                logger.error(
                    "GEMINI ERROR | "
                    "reasoning_agent | %s",
                    e
                )

                # =================================================
                # 10. RULE-BASED FALLBACK
                # =================================================

                if recommendation_service is not None:

                    try:

                        recommendation = (
                            recommendation_service
                            .generate_recommendation(
                                insight
                            )
                        )

                        if isinstance(
                            recommendation,
                            dict
                        ):

                            if hasattr(
                                insight,
                                "impact"
                            ):

                                insight.impact = (
                                    recommendation.get(
                                        "impact",
                                        getattr(
                                            insight,
                                            "impact",
                                            ""
                                        )
                                    )
                                )

                            if hasattr(
                                insight,
                                "recommendation"
                            ):

                                insight.recommendation = (
                                    recommendation.get(
                                        "recommendation",
                                        getattr(
                                            insight,
                                            "recommendation",
                                            ""
                                        )
                                    )
                                )

                        updated_insight = (
                            insight
                        )

                    except Exception as fallback_error:

                        logger.error(
                            "RECOMMENDATION FALLBACK ERROR | "
                            "%s",
                            fallback_error
                        )

                        updated_insight = (
                            insight
                        )

            updated_insights.append(
                updated_insight
            )

    # =========================================================
    # 11. FINAL EXECUTION METRICS
    # =========================================================

        execution_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AGENT END | reasoning_agent | "
            "execution_time=%.2fs | "
            "insights=%s | "
            "gemini_used=%s",
            execution_time,
            len(updated_insights),
            gemini_used
        )

        # =========================================================
        # 12. STRUCTURED AGENT OUTPUT
        # =========================================================

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
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
                    ),

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

        logger.info(
            "AGENT END | reasoning_agent"
        )

        # =========================================================
        # 13. RETURN UPDATED STATE
        # =========================================================

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
    # 14. COMPLETE AGENT FAILURE
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

        agent_outputs = dict(
            state.get(
                "agent_outputs",
                {}
            )
        )

        agent_outputs[
            "reasoning_agent"
        ] = {

            "agent": "reasoning_agent",

            "status": "failed",

            "output": None,

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