import logging
import time

from app.agents.state import AgentState
from app.services.risk_scoring_service import RiskScoringService
from app.services.sla_feature_service import SLAFeatureService
from app.services.sla_predictor import SLAPredictor


logger = logging.getLogger(__name__)


# =========================================================
# SLA SERVICES
# =========================================================

sla_feature_service = SLAFeatureService()
sla_predictor = SLAPredictor()


def _build_sla_features(
    workflow,
    all_workflows=None,
):
    """
    Convert a live Jira workflow record into
    the feature contract expected by SLAPredictor.
    """

    return sla_feature_service.build_features(
        workflow=workflow,
        all_workflows=all_workflows,
    )


def planner_agent(state: AgentState):
    """
    Creates a decomposed execution plan.

    Planner decides WHAT needs to be done.

    Planner does NOT:
    - execute Jira actions
    - mutate Jira
    - approve actions

    High-risk Jira actions are only proposed.
    Actual approval handling happens in plan_executor
    and the approval API.

    SLA prediction is generated here from the
    selected workflow using SLAFeatureService
    and SLAPredictor.
    """

    logger.info(
        "AGENT START | planner_agent"
    )

    start_time = time.perf_counter()

    try:

        # =====================================================
        # READ STATE
        # =====================================================

        intent = state.get(
            "intent"
        )

        user_goal = state.get(
            "user_goal"
        )

        workflows = list(
            state.get(
                "workflows",
                []
            )
        )

        existing_issue_key = state.get(
            "issue_key"
        )


        # =====================================================
        # DEFAULTS
        # =====================================================

        plan = []

        proposed_action = {}

        approval_required = False

        approval_status = None

        approval_reason = None

        issue_key = existing_issue_key

        sla_prediction = {

            "sla_breach_probability": None,

            "risk_level": "Unknown",

        }


        # =====================================================
        # RISK ANALYSIS
        # =====================================================

        risk_data = {

            "average_risk": 0,

            "high_risk_tickets": [],

            "tickets": []

        }


        try:

            risk_service = (
                RiskScoringService()
            )

            risk_data = (
                risk_service.calculate(
                    workflows
                )
            )

        except Exception as risk_error:

            logger.exception(
                "RISK ANALYSIS FAILED | %s",
                risk_error
            )


        # =====================================================
        # FIND HIGH-RISK TICKETS
        # =====================================================

        high_risk_tickets = [

            ticket

            for ticket in risk_data.get(
                "tickets",
                []
            )

            if ticket.get(
                "risk_level"
            ) == "High"

        ]


        # =====================================================
        # SELECT HIGHEST-RISK TICKET
        #
        # IMPORTANT:
        # Select maximum risk score rather than
        # simply taking the first High-risk ticket.
        # =====================================================

        selected_high_risk = None

        if high_risk_tickets:

            selected_high_risk = max(

                high_risk_tickets,

                key=lambda ticket:
                    ticket.get(
                        "risk_score",
                        0
                    )

            )


        # =====================================================
        # SET ISSUE KEY
        # =====================================================

        if selected_high_risk:

            selected_issue_key = (
                selected_high_risk.get(
                    "ticket_id"
                )
            )

            # Preserve an explicitly supplied issue key.
            if not issue_key:

                issue_key = (
                    selected_issue_key
                )

            logger.info(

                "HIGH-RISK TICKET DETECTED | "
                "selected=%s | score=%s",

                issue_key,

                selected_high_risk.get(
                    "risk_score"
                )

            )


        # =====================================================
        # SLA PREDICTION
        #
        # Generate prediction for the selected
        # highest-risk workflow.
        # =====================================================

        selected_workflow = None


        if workflows:

            # First try to match the selected issue key.
            if issue_key:

                for workflow in workflows:

                    workflow_issue_key = (
                        workflow.get(
                            "ticket_id"
                        )
                        if isinstance(
                            workflow,
                            dict
                        )
                        else None
                    )

                    if (
                        workflow_issue_key
                        == issue_key
                    ):

                        selected_workflow = (
                            workflow
                        )

                        break


            # If no matching workflow was found,
            # use the highest-risk ticket when available.
            if selected_workflow is None:

                if selected_high_risk:

                    selected_issue_key = (
                        selected_high_risk.get(
                            "ticket_id"
                        )
                    )

                    for workflow in workflows:

                        workflow_issue_key = (
                            workflow.get(
                                "ticket_id"
                            )
                            if isinstance(
                                workflow,
                                dict
                            )
                            else None
                        )

                        if (
                            workflow_issue_key
                            == selected_issue_key
                        ):

                            selected_workflow = (
                                workflow
                            )

                            break


            # Final fallback.
            if selected_workflow is None:

                selected_workflow = (
                    workflows[0]
                )


        if selected_workflow:

            try:

                sla_features = (
                    _build_sla_features(
                        selected_workflow,
                        workflows,
                    )
                )

                logger.info(
                    "SLA FEATURES BUILT | "
                    "ticket=%s | features=%s",
                    issue_key,
                    sla_features
                )


                sla_prediction = (
                    sla_predictor.predict(
                        sla_features
                    )
                )


                logger.info(
                    "SLA PREDICTION | "
                    "ticket=%s | probability=%.4f | "
                    "risk=%s",

                    issue_key,

                    sla_prediction.get(
                        "sla_breach_probability",
                        0
                    ),

                    sla_prediction.get(
                        "risk_level"
                    )
                )


            except Exception as sla_error:

                logger.exception(
                    "SLA PREDICTION FAILED | %s",
                    sla_error
                )

                sla_prediction = {

                    "sla_breach_probability":
                        None,

                    "risk_level":
                        "Unknown",

                    "error":
                        str(
                            sla_error
                        )

                }


        else:

            logger.warning(
                "SLA PREDICTION SKIPPED | "
                "no workflow available"
            )


        # =====================================================
        # EXPLAIN DELAY
        # =====================================================

        if intent == "explain_delay":

            plan = [

                "find_workflow",

                "find_delayed_tasks",

                "retrieve_jira_evidence",

                "retrieve_slack_evidence",

                "compare_evidence",

                "observe",

                "identify_root_causes",

                "generate_recommendations"

            ]


        # =====================================================
        # ANALYZE WORKFLOW
        # =====================================================

        elif intent == "analyze_workflow":

            plan = [

                "find_workflow",

                "detect_patterns",

                "find_delayed_tasks",

                "retrieve_jira_evidence",

                "retrieve_slack_evidence",

                "compare_evidence",

                "observe",

                "identify_root_causes",

                "generate_recommendations"

            ]


            # -------------------------------------------------
            # Add HITL proposal only when a High-risk ticket
            # exists.
            # -------------------------------------------------

            if selected_high_risk:

                plan.append(
                    "propose_jira_change"
                )


        # =====================================================
        # FIND BOTTLENECK
        # =====================================================

        elif intent == "find_bottleneck":

            plan = [

                "find_workflow",

                "detect_patterns",

                "find_delayed_tasks",

                "retrieve_jira_evidence",

                "retrieve_slack_evidence",

                "compare_evidence",

                "observe",

                "identify_bottlenecks",

                "generate_recommendations"

            ]


        # =====================================================
        # RECOMMEND ACTION
        # =====================================================

        elif intent == "recommend_action":

            plan = [

                "find_workflow",

                "identify_problem",

                "retrieve_jira_evidence",

                "retrieve_slack_evidence",

                "compare_evidence",

                "observe",

                "identify_root_causes",

                "generate_recommendations"

            ]


            if selected_high_risk:

                plan.append(
                    "propose_jira_change"
                )


        # =====================================================
        # RETRIEVE JIRA ISSUE
        # =====================================================

        elif intent == "retrieve_jira_issue":

            plan = [

                "extract_issue_key",

                "retrieve_jira_issue",

                "return_issue"

            ]


        # =====================================================
        # UNKNOWN INTENT
        # =====================================================

        else:

            plan = [
                "understand_goal"
            ]


        # =====================================================
        # LOG PLAN
        # =====================================================

        logger.info(

            "PLAN CREATED | intent=%s | steps=%s",

            intent,

            len(plan)

        )


        logger.info(

            "TASK DECOMPOSITION | plan=%s",

            plan

        )


        logger.info(

            "RISK SUMMARY | average=%s | high_risk=%s",

            risk_data.get(
                "average_risk"
            ),

            risk_data.get(
                "high_risk_tickets"
            )

        )


        logger.info(

            "SLA SUMMARY | probability=%s | risk=%s",

            sla_prediction.get(
                "sla_breach_probability"
            ),

            sla_prediction.get(
                "risk_level"
            )

        )


        logger.info(

            "HUMAN-IN-THE-LOOP | "
            "required=%s | "
            "status=%s | "
            "issue=%s",

            approval_required,

            approval_status,

            issue_key

        )


        # =====================================================
        # EXECUTION TIME
        # =====================================================

        execution_time = (
            time.perf_counter()
            - start_time
        )


        # =====================================================
        # STRUCTURED AGENT OUTPUT
        # =====================================================

        agent_outputs = dict(

            state.get(
                "agent_outputs",
                {}
            )

        )


        agent_outputs[
            "planner_agent"
        ] = {

            "agent":
                "planner_agent",

            "status":
                "success",

            "output": {

                "intent":
                    intent,

                "plan":
                    plan,

                "steps":
                    len(plan),

                "high_risk_tickets":
                    high_risk_tickets,

                "selected_issue_key":
                    issue_key,

                "selected_risk_score":
                    (
                        selected_high_risk.get(
                            "risk_score"
                        )
                        if selected_high_risk
                        else None
                    ),

                "sla_prediction":
                    sla_prediction,

                "proposed_action":
                    proposed_action,

                "approval_required":
                    approval_required,

                "approval_status":
                    approval_status,

                "approval_reason":
                    approval_reason

            },

            "execution_time":
                execution_time,

            "error":
                None

        }


        logger.info(

            "STRUCTURED OUTPUT | "
            "agent=planner_agent | "
            "status=success"

        )


        logger.info(
            "AGENT END | planner_agent"
        )


        # =====================================================
        # RETURN STATE
        # =====================================================

        return {

            "user_goal":
                user_goal,

            "intent":
                intent,

            "plan":
                plan,

            "current_step":
                0,

            "issue_key":
                issue_key,

            "sla_prediction":
                sla_prediction,

            "proposed_action":
                proposed_action,

            "approval_required":
                approval_required,

            "approval_status":
                approval_status,

            "approval_reason":
                approval_reason,

            "execution_status":
                None,

            "execution_error":
                None,

            "goal_completed":
                False,

            "termination_reason":
                None,

            "agent_outputs":
                agent_outputs

        }


    # =========================================================
    # ERROR
    # =========================================================

    except Exception as e:

        execution_time = (
            time.perf_counter()
            - start_time
        )


        logger.exception(

            "AGENT FAILED | planner_agent | "
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
            "planner_agent"
        ] = {

            "agent":
                "planner_agent",

            "status":
                "failed",

            "output":
                None,

            "execution_time":
                execution_time,

            "error":
                str(e)

        }


        errors = list(

            state.get(
                "errors",
                []
            )

        )


        errors.append({

            "agent":
                "planner_agent",

            "error":
                str(e)

        })


        return {

            "agent_outputs":
                agent_outputs,

            "errors":
                errors,

            "execution_status":
                "failed",

            "execution_error":
                str(e)

        }