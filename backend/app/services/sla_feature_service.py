from datetime import datetime


class SLAFeatureService:

    FEATURE_COLUMNS = [
        "customer_tenure_months",
        "previous_tickets_90d",
        "avg_sentiment_score",
        "message_length",
        "contains_urgent_keyword",
        "contains_refund_keyword",
        "agent_queue_length_at_submit",
        "agent_experience_months",
        "backlog_age_hours",
        "response_time_hours",
        "waiting_ratio",
        "blocker_density",
        "reassignment_rate",
        "dependency_count",
        "workflow_complexity",
    ]

    # =========================================================
    # HELPER: GET VALUE FROM DICT OR OBJECT
    # =========================================================

    def _get(
        self,
        workflow,
        *names,
        default=None
    ):

        if isinstance(workflow, dict):

            for name in names:

                if name in workflow:
                    return workflow[name]

        for name in names:

            if hasattr(workflow, name):

                return getattr(
                    workflow,
                    name
                )

        return default

    # =========================================================
    # HELPER: SAFE FLOAT
    # =========================================================

    def _to_float(
        self,
        value,
        default=0.0
    ):

        try:

            if value is None:
                return default

            return float(value)

        except (
            TypeError,
            ValueError
        ):

            return default

    # =========================================================
    # HELPER: KEYWORD CHECK
    # =========================================================

    def _contains_keyword(
        self,
        text,
        keywords
    ):

        text = str(
            text or ""
        ).lower()

        return float(
            any(
                keyword in text
                for keyword in keywords
            )
        )

    # =========================================================
    # HELPER: PARSE DATETIME
    # =========================================================

    def _parse_datetime(
        self,
        value
    ):

        if not value:
            return None

        if isinstance(
            value,
            datetime
        ):
            return value

        try:

            return datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    "+00:00"
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return None

    # =========================================================
    # AGENT QUEUE
    # =========================================================

    def _calculate_agent_queue(
        self,
        workflow,
        all_workflows
    ):

        assignee = self._get(
            workflow,
            "assignee",
            default=None
        )

        if not assignee:
            return 0.0

        queue = 0

        for item in all_workflows:

            item_assignee = self._get(
                item,
                "assignee",
                default=None
            )

            if (
                item_assignee
                and str(
                    item_assignee
                ).lower()
                == str(
                    assignee
                ).lower()
            ):

                status = str(
                    self._get(
                        item,
                        "status",
                        default=""
                    )
                    or ""
                ).lower()

                if status not in [
                    "done",
                    "closed",
                    "resolved"
                ]:

                    queue += 1

        return float(queue)

    # =========================================================
    # PREVIOUS TICKETS
    # =========================================================

    def _calculate_previous_tickets(
        self,
        workflow,
        all_workflows
    ):

        customer_id = self._get(
            workflow,
            "customer_id",
            "customer",
            "customerId",
            default=None
        )

        if not customer_id:
            return 0.0

        current_created = self._parse_datetime(
            self._get(
                workflow,
                "created_at",
                "created",
                default=None
            )
        )

        if current_created is None:
            return 0.0

        count = 0

        for item in all_workflows:

            if item is workflow:
                continue

            item_customer = self._get(
                item,
                "customer_id",
                "customer",
                "customerId",
                default=None
            )

            if not item_customer:
                continue

            if str(
                item_customer
            ).lower() != str(
                customer_id
            ).lower():

                continue

            item_created = self._parse_datetime(
                self._get(
                    item,
                    "created_at",
                    "created",
                    default=None
                )
            )

            if item_created is None:
                continue

            delta = (
                current_created
                - item_created
            ).total_seconds()

            if (
                0
                < delta
                <= 90 * 24 * 60 * 60
            ):

                count += 1

        return float(count)

    # =========================================================
    # BUILD SLA FEATURES
    # =========================================================

    def build_features(
        self,
        workflow,
        all_workflows=None
    ):

        # -----------------------------------------------------
        # IMPORTANT:
        # Workflow can be a WorkflowRecord object OR a dict.
        # Do not reject object-based workflows.
        # -----------------------------------------------------

        all_workflows = (
            all_workflows
            if isinstance(
                all_workflows,
                list
            )
            else []
        )

        # =====================================================
        # BASIC WORKFLOW VALUES
        # =====================================================

        title = self._get(
            workflow,
            "title",
            "summary",
            default=""
        )

        priority = str(
            self._get(
                workflow,
                "priority",
                default=""
            )
            or ""
        ).lower()

        status = str(
            self._get(
                workflow,
                "status",
                default=""
            )
            or ""
        ).lower()

        days_waiting = self._to_float(
            self._get(
                workflow,
                "days_waiting",
                default=0
            )
        )

        # =====================================================
        # BACKLOG AGE
        # =====================================================

        backlog_age_hours = (
            days_waiting * 24
        )

        explicit_backlog = self._get(
            workflow,
            "backlog_age_hours",
            default=None
        )

        if explicit_backlog is not None:

            backlog_age_hours = self._to_float(
                explicit_backlog,
                backlog_age_hours
            )

        # =====================================================
        # RESPONSE TIME
        # =====================================================

        response_time_hours = (
            self._to_float(
                self._get(
                    workflow,
                    "response_time_hours",
                    default=None
                )
            )
        )

        if response_time_hours <= 0:

            first_response_minutes = (
                self._to_float(
                    self._get(
                        workflow,
                        "first_response_minutes",
                        default=None
                    )
                )
            )

            if first_response_minutes > 0:

                response_time_hours = (
                    first_response_minutes / 60
                )

        # -----------------------------------------------------
        # Controlled fallback when Jira does not provide
        # response-time information.
        # -----------------------------------------------------

        if response_time_hours <= 0:

            response_time_hours = min(
                backlog_age_hours,
                24
            )

        # =====================================================
        # WAITING RATIO
        # =====================================================

        waiting_ratio = (
            backlog_age_hours
            / (
                backlog_age_hours
                + response_time_hours
                + 1e-6
            )
        )

        # =====================================================
        # MESSAGE LENGTH
        # =====================================================

        message_length = self._to_float(
            self._get(
                workflow,
                "message_length",
                default=len(
                    str(title)
                )
            )
        )

        # =====================================================
        # KEYWORD FLAGS
        # =====================================================

        contains_urgent_keyword = (
            self._contains_keyword(
                title,
                [
                    "urgent",
                    "critical",
                    "immediately",
                    "asap",
                    "emergency"
                ]
            )
        )

        contains_refund_keyword = (
            self._contains_keyword(
                title,
                [
                    "refund",
                    "reimbursement",
                    "money back",
                    "return"
                ]
            )
        )

        # =====================================================
        # AGENT QUEUE
        # =====================================================

        agent_queue_length_at_submit = (
            self._calculate_agent_queue(
                workflow,
                all_workflows
            )
        )

        explicit_queue = self._get(
            workflow,
            "agent_queue_length_at_submit",
            "queue_length",
            default=None
        )

        if explicit_queue is not None:

            agent_queue_length_at_submit = (
                self._to_float(
                    explicit_queue,
                    agent_queue_length_at_submit
                )
            )

        # =====================================================
        # PREVIOUS TICKETS
        # =====================================================

        previous_tickets_90d = (
            self._calculate_previous_tickets(
                workflow,
                all_workflows
            )
        )

        explicit_previous = self._get(
            workflow,
            "previous_tickets_90d",
            default=None
        )

        if explicit_previous is not None:

            previous_tickets_90d = (
                self._to_float(
                    explicit_previous,
                    previous_tickets_90d
                )
            )

        # =====================================================
        # REOPENED
        # =====================================================

        reopened_last_90d = (
            self._to_float(
                self._get(
                    workflow,
                    "reopened_last_90d",
                    default=0
                )
            )
        )

        if (
            reopened_last_90d == 0
            and "reopen" in status
        ):

            reopened_last_90d = 1.0

        # =====================================================
        # BLOCKER DENSITY
        # =====================================================

        blocker_density = (
            self._to_float(
                self._get(
                    workflow,
                    "blocker_density",
                    default=0
                )
            )
        )

        if (
            blocker_density == 0
            and (
                "blocked" in status
                or "blocker" in str(title).lower()
            )
        ):

            blocker_density = 1.0

        # =====================================================
        # REASSIGNMENT RATE
        # =====================================================

        reassignment_rate = (
            self._to_float(
                self._get(
                    workflow,
                    "reassignment_rate",
                    default=0
                )
            )
        )

        # =====================================================
        # DEPENDENCY COUNT
        # =====================================================

        dependency_count = (
            self._to_float(
                self._get(
                    workflow,
                    "dependency_count",
                    "dependencies",
                    default=0
                )
            )
        )

        # =====================================================
        # WORKFLOW COMPLEXITY
        # =====================================================

        priority_weight = {
            "highest": 5,
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "lowest": 1
        }.get(
            priority,
            1
        )

        workflow_complexity = (
            agent_queue_length_at_submit
            + previous_tickets_90d
            + reopened_last_90d
            + priority_weight
            + blocker_density
            + dependency_count
        )

        explicit_complexity = self._get(
            workflow,
            "workflow_complexity",
            default=None
        )

        if explicit_complexity is not None:

            workflow_complexity = (
                self._to_float(
                    explicit_complexity,
                    workflow_complexity
                )
            )

        # =====================================================
        # FEATURES NOT AVAILABLE DIRECTLY FROM JIRA
        # =====================================================

        customer_tenure_months = (
            self._to_float(
                self._get(
                    workflow,
                    "customer_tenure_months",
                    default=0
                )
            )
        )

        avg_sentiment_score = (
            self._to_float(
                self._get(
                    workflow,
                    "avg_sentiment_score",
                    "sentiment_score",
                    default=0
                )
            )
        )

        agent_experience_months = (
            self._to_float(
                self._get(
                    workflow,
                    "agent_experience_months",
                    default=0
                )
            )
        )

        # =====================================================
        # FINAL FEATURE DICTIONARY
        # =====================================================

        features = {

            "customer_tenure_months":
                customer_tenure_months,

            "previous_tickets_90d":
                previous_tickets_90d,

            "avg_sentiment_score":
                avg_sentiment_score,

            "message_length":
                message_length,

            "contains_urgent_keyword":
                contains_urgent_keyword,

            "contains_refund_keyword":
                contains_refund_keyword,

            "agent_queue_length_at_submit":
                agent_queue_length_at_submit,

            "agent_experience_months":
                agent_experience_months,

            "backlog_age_hours":
                backlog_age_hours,

            "response_time_hours":
                response_time_hours,

            "waiting_ratio":
                waiting_ratio,

            "blocker_density":
                blocker_density,

            "reassignment_rate":
                reassignment_rate,

            "dependency_count":
                dependency_count,

            "workflow_complexity":
                workflow_complexity
        }

        return features