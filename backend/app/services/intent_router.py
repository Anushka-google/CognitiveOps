import logging

from app.agents.pattern_agent import (
    pattern_agent
)

from app.agents.workflow_agent import (
    workflow_agent
)

from app.agents.recommendation_agent import (
    recommendation_agent
)

from app.agents.planner_agent import (
    planner_agent
)

from app.agents.reasoning_agent import (
    reasoning_agent
)

from app.services.workflow_analyzer import (
    WorkflowAnalyzer
)


logger = logging.getLogger(__name__)


class IntentRouter:
    """
    Routes a detected user intent
    to the appropriate CognitiveOps
    processing flow.
    """

    def route(
        self,
        intent_result,
        workflows,
        question
    ):

        logger.info(
            "INTENT ROUTER START | "
            "intent=%s | confidence=%.2f",
            intent_result.intent.value,
            intent_result.confidence
        )

        # =====================================================
        # GET INTENT
        # =====================================================

        intent = (
            intent_result.intent.value
        )

        # =====================================================
        # PLANNING
        # =====================================================

        planning_state = {
            "user_goal": question,
            "intent": intent
        }

        plan_result = planner_agent(
            planning_state
        )

        plan = plan_result.get(
            "plan",
            []
        )

        logger.info(
            "PLAN GENERATED | "
            "intent=%s | steps=%s",
            intent,
            len(plan)
        )

        # =====================================================
        # ANALYZE WORKFLOW
        # =====================================================

        if intent == "analyze_workflow":

            logger.info(
                "ROUTING | analyze_workflow"
            )

            state = {
                "workflows": workflows,
                "insights": []
            }

            # -----------------------------------------------
            # Pattern Detection
            # -----------------------------------------------

            pattern_result = pattern_agent(
                state
            )

            state.update(
                pattern_result
            )

            # -----------------------------------------------
            # Workflow Analysis
            # -----------------------------------------------

            workflow_result = workflow_agent(
                state
            )

            state.update(
                workflow_result
            )

            # -----------------------------------------------
            # Recommendations
            # -----------------------------------------------

            recommendation_result = (
                recommendation_agent(
                    state
                )
            )

            state.update(
                recommendation_result
            )

            return {
                "intent": intent,
                "action": "analyze_workflow",
                "plan": plan,
                "result": state.get(
                    "insights",
                    []
                ),
                "workflow_summary": state.get(
                    "workflow_summary"
                ),
                "workflow_health": state.get(
                    "workflow_health"
                ),
                "total_issues": state.get(
                    "total_issues",
                    0
                ),
                "high_severity_issues": state.get(
                    "high_severity_issues",
                    0
                )
            }

        # =====================================================
        # FIND BOTTLENECK
        # =====================================================

        if intent == "find_bottleneck":

            logger.info(
                "ROUTING | find_bottleneck"
            )

            analyzer = WorkflowAnalyzer()

            insights = (
                analyzer.detect_delays(
                    workflows
                )
            )

            return {
                "intent": intent,
                "action": "find_bottleneck",
                "plan": plan,
                "result": insights
            }

        # =====================================================
        # EXPLAIN DELAY
        # =====================================================

        if intent == "explain_delay":

            logger.info(
                "ROUTING | explain_delay"
            )

            # -----------------------------------------------
            # Step 1: Extract Jira Issue Key
            # -----------------------------------------------

            issue_key = (
                self._extract_issue_key(
                    question
                )
            )

            logger.info(
                "ISSUE KEY EXTRACTED | key=%s",
                issue_key
            )

            # -----------------------------------------------
            # Step 2: Filter Jira Workflow
            # -----------------------------------------------

            filtered_workflows = (
                self._filter_workflows(
                    workflows,
                    issue_key
                )
            )

            logger.info(
                "DELAY WORKFLOW FILTER | "
                "requested=%s | matched=%s",
                issue_key,
                len(filtered_workflows)
            )

            # -----------------------------------------------
            # No Jira issue found
            # -----------------------------------------------

            if not filtered_workflows:

                logger.warning(
                    "NO WORKFLOW FOUND | "
                    "issue=%s",
                    issue_key
                )

                return {
                    "intent": intent,
                    "action": "explain_delay",
                    "plan": plan,
                    "result": []
                }

            # -----------------------------------------------
            # Step 3: Create Agent State
            # -----------------------------------------------

            state = {
                "workflows": filtered_workflows,
                "insights": []
            }

            # -----------------------------------------------
            # Step 4: Pattern Agent
            #
            # Detects operational problem
            # Example:
            # Approval Delay
            # Waiting: 70 days
            # -----------------------------------------------

            pattern_result = pattern_agent(
                state
            )

            state.update(
                pattern_result
            )

            logger.info(
                "PATTERN ANALYSIS COMPLETE | "
                "insights=%s",
                len(
                    state.get(
                        "insights",
                        []
                    )
                )
            )

            # -----------------------------------------------
            # Step 5: Reasoning Agent
            #
            # Uses Gemini + RAG context
            # to generate:
            #
            # root_cause
            # impact
            # recommendation
            # -----------------------------------------------

            reasoning_result = reasoning_agent(
                state
            )

            state.update(
                reasoning_result
            )

            logger.info(
                "REASONING COMPLETE | "
                "insights=%s",
                len(
                    state.get(
                        "insights",
                        []
                    )
                )
            )

            # -----------------------------------------------
            # Step 6: Final Result
            # -----------------------------------------------

            return {
                "intent": intent,
                "action": "explain_delay",
                "plan": plan,
                "result": state.get(
                    "insights",
                    []
                )
            }

        # =====================================================
        # RECOMMEND ACTION
        # =====================================================

        if intent == "recommend_action":

            logger.info(
                "ROUTING | recommend_action"
            )

            state = {
                "workflows": workflows,
                "insights": []
            }

            # -----------------------------------------------
            # Pattern Detection
            # -----------------------------------------------

            pattern_result = pattern_agent(
                state
            )

            state.update(
                pattern_result
            )

            # -----------------------------------------------
            # Recommendation
            # -----------------------------------------------

            recommendation_result = (
                recommendation_agent(
                    state
                )
            )

            state.update(
                recommendation_result
            )

            return {
                "intent": intent,
                "action": "recommend_action",
                "plan": plan,
                "result": state.get(
                    "insights",
                    []
                )
            }

        # =====================================================
        # RETRIEVE JIRA ISSUE
        # =====================================================

        if intent == "retrieve_jira_issue":

            logger.info(
                "ROUTING | retrieve_jira_issue"
            )

            issue_key = (
                self._extract_issue_key(
                    question
                )
            )

            filtered_workflows = (
                self._filter_workflows(
                    workflows,
                    issue_key
                )
            )

            return {
                "intent": intent,
                "action": "retrieve_jira_issue",
                "plan": plan,
                "result": filtered_workflows
            }

        # =====================================================
        # UNKNOWN INTENT
        # =====================================================

        logger.warning(
            "UNKNOWN INTENT | intent=%s",
            intent
        )

        return {
            "intent": intent,
            "action": "unknown",
            "plan": plan,
            "result": []
        }

    # =========================================================
    # EXTRACT JIRA ISSUE KEY
    # =========================================================

    def _extract_issue_key(
        self,
        question
    ):

        import re

        if not question:

            return None

        match = re.search(
            r"\b[A-Z][A-Z0-9]+-\d+\b",
            question.upper()
        )

        if not match:

            return None

        return match.group(0)

    # =========================================================
    # FILTER WORKFLOWS BY JIRA ISSUE KEY
    # =========================================================

    def _filter_workflows(
        self,
        workflows,
        issue_key
    ):

        if not issue_key:

            logger.info(
                "NO ISSUE KEY FOUND | "
                "using all workflows"
            )

            return workflows

        requested_key = str(
            issue_key
        ).strip().upper()

        filtered = []

        for workflow in workflows:

            workflow_key = str(
                getattr(
                    workflow,
                    "ticket_id",
                    ""
                )
            ).strip().upper()

            logger.info(
                "WORKFLOW CHECK | "
                "requested=%s | current=%s",
                requested_key,
                workflow_key
            )

            if workflow_key == requested_key:

                filtered.append(
                    workflow
                )

        logger.info(
            "WORKFLOW FILTER | "
            "requested=%s | matched=%s",
            requested_key,
            len(filtered)
        )

        return filtered