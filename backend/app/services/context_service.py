class ContextService:
    """Builds structured context for LLM analysis."""

    def build_insight_context(
        self,
        insight,
        retrieved_context: str | None = None,
        user_request: str | None = None,
        agent_state: dict | None = None
    ) -> str:
        """
        Build prioritized context for LLM analysis.

        Context sources:
        1. Current operational insight
        2. Existing insight evidence
        3. Jira evidence
        4. Slack evidence
        5. Optional user request
        6. Existing analysis
        7. Optional workflow state
        8. Retrieved RAG knowledge
        """

        context_parts = []

        # --------------------------------
        # 1. Current Operational Context
        # --------------------------------

        context_parts.append(
            f"ISSUE:\n{insight.issue}"
        )

        context_parts.append(
            f"SEVERITY:\n{insight.severity}"
        )

        # --------------------------------
        # 2. Existing Insight Evidence
        # --------------------------------

        relevant_evidence = [
            item
            for item in insight.evidence
            if item and item.strip()
        ]

        evidence_text = "\n".join(
            f"- {item}"
            for item in relevant_evidence
        )

        context_parts.append(
            f"EVIDENCE:\n{evidence_text}"
        )

        # --------------------------------
        # 3. Jira + Slack Evidence
        # --------------------------------

        if agent_state:

            jira_evidence = (
                agent_state.get(
                    "jira",
                    []
                )
            )

            slack_evidence = (
                agent_state.get(
                    "slack",
                    []
                )
            )

            # ----------------------------
            # Jira
            # ----------------------------

            if jira_evidence:

                jira_text = "\n".join(
                    f"- {item}"
                    for item in jira_evidence
                )

                context_parts.append(
                    "JIRA EVIDENCE:\n"
                    f"{jira_text}"
                )

            else:

                context_parts.append(
                    "JIRA EVIDENCE:\n"
                    "No Jira evidence found."
                )

            # ----------------------------
            # Slack
            # ----------------------------

            if slack_evidence:

                slack_lines = []

                for item in slack_evidence:

                    if isinstance(
                        item,
                        dict
                    ):

                        message = str(
                            item.get(
                                "message",
                                ""
                            )
                        ).strip()

                        timestamp = str(
                            item.get(
                                "timestamp",
                                ""
                            )
                        ).strip()

                        if timestamp:

                            slack_lines.append(
                                f"- {message} "
                                f"(timestamp: {timestamp})"
                            )

                        else:

                            slack_lines.append(
                                f"- {message}"
                            )

                    else:

                        slack_lines.append(
                            f"- {item}"
                        )

                slack_text = "\n".join(
                    slack_lines
                )

                context_parts.append(
                    "SLACK EVIDENCE:\n"
                    f"{slack_text}"
                )

            else:

                context_parts.append(
                    "SLACK EVIDENCE:\n"
                    "No Slack evidence found."
                )

        # --------------------------------
        # 4. Optional User Request
        # --------------------------------

        if user_request:

            context_parts.append(
                f"USER REQUEST:\n"
                f"{user_request}"
            )

        # --------------------------------
        # 5. Existing Analysis
        # --------------------------------

        if insight.root_cause:

            context_parts.append(
                f"ROOT CAUSE:\n"
                f"{insight.root_cause}"
            )

        if insight.impact:

            context_parts.append(
                f"IMPACT:\n"
                f"{insight.impact}"
            )

        if insight.recommendation:

            context_parts.append(
                f"RECOMMENDATION:\n"
                f"{insight.recommendation}"
            )

        # --------------------------------
        # 6. Optional Agent State
        # --------------------------------

        if agent_state:

            relevant_state = {}

            for key in [
                "workflow_summary",
                "workflow_health",
                "total_issues",
                "high_severity_issues"
            ]:

                if key in agent_state:

                    relevant_state[key] = (
                        agent_state[key]
                    )

            if relevant_state:

                state_text = "\n".join(
                    f"{key}: {value}"
                    for key, value
                    in relevant_state.items()
                )

                context_parts.append(
                    f"AGENT STATE:\n"
                    f"{state_text}"
                )

        # --------------------------------
        # 7. Retrieved RAG Knowledge
        # --------------------------------

        if retrieved_context:

            context_parts.append(
                "RETRIEVED KNOWLEDGE:\n"
                f"{retrieved_context}"
            )

        else:

            context_parts.append(
                "RETRIEVED KNOWLEDGE:\n"
                "No relevant knowledge was found."
            )

        # --------------------------------
        # 8. Final Context
        # --------------------------------

        final_context = "\n\n".join(
            context_parts
        )

        # --------------------------------
        # Debug
        # --------------------------------

        print(
            "\n=================================="
        )

        print(
            "LLM CONTEXT"
        )

        print(
            "=================================="
        )

        print(
            final_context
        )

        print(
            "==================================\n"
        )

        return final_context