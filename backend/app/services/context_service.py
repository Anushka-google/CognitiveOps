from app.config import LLM_MAX_CONTEXT_LENGTH


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
        8. Root cause graph
        9. Long-term memory
        10. Retrieved RAG knowledge
        """

        context_parts = []

        # =================================================
        # CURRENT OPERATIONAL INSIGHT
        # =================================================

        context_parts.append(
            f"ISSUE:\n{insight.issue}"
        )

        context_parts.append(
            f"SEVERITY:\n{insight.severity}"
        )

        # =================================================
        # INSIGHT EVIDENCE
        # =================================================

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

        # =================================================
        # JIRA + SLACK EVIDENCE
        # =================================================

        if agent_state:

            jira_evidence = agent_state.get(
                "jira",
                agent_state.get(
                    "jira_evidence",
                    []
                )
            )

            slack_evidence = agent_state.get(
                "slack",
                agent_state.get(
                    "slack_evidence",
                    []
                )
            )

            # -------------------------------------------------
            # JIRA
            # -------------------------------------------------

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

            # -------------------------------------------------
            # SLACK
            # -------------------------------------------------

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

        # =================================================
        # USER REQUEST
        # =================================================

        if user_request:

            context_parts.append(
                f"USER REQUEST:\n{user_request}"
            )

        # =================================================
        # EXISTING ANALYSIS
        # =================================================

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

        # =================================================
        # AGENT STATE
        # =================================================

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
                    "AGENT STATE:\n"
                    f"{state_text}"
                )

        # =================================================
        # ROOT CAUSE GRAPH
        # =================================================
        #
        # This is the main Phase 5.2 addition.
        #
        # The graph contains:
        # - workflow nodes
        # - owner nodes
        # - service nodes
        # - dependency relationships
        #
        # The LLM can now use these relationships when
        # explaining the root cause.
        # =================================================

        if agent_state:

            root_cause_graph = (
                agent_state.get(
                    "root_cause_graph",
                    {}
                )
            )

            if root_cause_graph:

                nodes = (
                    root_cause_graph.get(
                        "nodes",
                        []
                    )
                )

                edges = (
                    root_cause_graph.get(
                        "edges",
                        []
                    )
                )

                node_lines = []

                for node in nodes:

                    node_id = node.get(
                        "id",
                        "Unknown"
                    )

                    node_type = node.get(
                        "type",
                        "Unknown"
                    )

                    label = node.get(
                        "label",
                        node_id
                    )

                    node_lines.append(
                        f"- {node_id} "
                        f"| type={node_type} "
                        f"| label={label}"
                    )

                edge_lines = []

                for edge in edges:

                    source = edge.get(
                        "source",
                        "Unknown"
                    )

                    target = edge.get(
                        "target",
                        "Unknown"
                    )

                    relationship = edge.get(
                        "relationship",
                        "related_to"
                    )

                    edge_lines.append(
                        f"- {source} "
                        f"--{relationship}--> "
                        f"{target}"
                    )

                graph_text = (
                    "ROOT CAUSE GRAPH:\n"
                    "\n"
                    "NODES:\n"
                    +
                    (
                        "\n".join(
                            node_lines
                        )
                        if node_lines
                        else
                        "- No graph nodes found."
                    )
                    +
                    "\n\n"
                    "RELATIONSHIPS:\n"
                    +
                    (
                        "\n".join(
                            edge_lines
                        )
                        if edge_lines
                        else
                        "- No graph relationships found."
                    )
                )

                context_parts.append(
                    graph_text
                )

            else:

                context_parts.append(
                    "ROOT CAUSE GRAPH:\n"
                    "No root cause graph available."
                )

        else:

            context_parts.append(
                "ROOT CAUSE GRAPH:\n"
                "No root cause graph available."
            )

        # =================================================
        # LONG-TERM MEMORY
        # =================================================

        if agent_state:

            long_term_memory = (
                agent_state.get(
                    "long_term_memory",
                    []
                )
            )

            if long_term_memory:

                memory_lines = []

                for memory in (
                    long_term_memory
                ):

                    if isinstance(
                        memory,
                        str
                    ):

                        memory_lines.append(
                            f"- {memory}"
                        )

                    else:

                        memory_lines.append(
                            f"- {memory}"
                        )

                memory_text = "\n".join(
                    memory_lines
                )

                context_parts.append(
                    "LONG-TERM MEMORY:\n"
                    f"{memory_text}"
                )

            else:

                context_parts.append(
                    "LONG-TERM MEMORY:\n"
                    "No previous workflow memory found."
                )

        else:

            context_parts.append(
                "LONG-TERM MEMORY:\n"
                "No previous workflow memory found."
            )

        # =================================================
        # RETRIEVED RAG KNOWLEDGE
        # =================================================

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

        # =================================================
        # FINAL CONTEXT
        # =================================================

        final_context = "\n\n".join(
            context_parts
        )

        # =================================================
        # CONTEXT LIMIT
        # =================================================

        if (
            len(final_context)
            >
            LLM_MAX_CONTEXT_LENGTH
        ):

            final_context = (
                final_context[
                    :LLM_MAX_CONTEXT_LENGTH
                ]
                +
                "\n\n"
                "[CONTEXT TRUNCATED DUE TO SIZE LIMIT]"
            )

        # =================================================
        # DEBUG LOG
        # =================================================

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