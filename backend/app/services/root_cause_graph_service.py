class RootCauseGraphService:

    def build_graph(self, issues):
        nodes = []
        edges = []

        node_ids = set()

        def add_node(
            node_id,
            node_type,
            label,
            metadata=None
        ):
            if node_id in node_ids:
                return

            node_ids.add(node_id)

            nodes.append({
                "id": node_id,
                "type": node_type,
                "label": label,
                "metadata": metadata or {}
            })

        for issue in issues:

            issue_key = issue.get(
                "key",
                "Unknown"
            )

            fields = issue.get(
                "fields",
                {}
            )

            summary = fields.get(
                "summary",
                "Untitled issue"
            )

            status = (
                fields.get("status") or {}
            ).get(
                "name",
                "Unknown"
            )

            priority = (
                fields.get("priority") or {}
            ).get(
                "name",
                "Unknown"
            )

            assignee = (
                fields.get("assignee") or {}
            ).get(
                "displayName"
            )

            project = (
                fields.get("project") or {}
            ).get(
                "name"
            )

            components = (
                fields.get("components") or []
            )

            # =============================================
            # ISSUE NODE
            # =============================================

            add_node(
                issue_key,
                "workflow",
                summary,
                {
                    "ticket_id": issue_key,
                    "status": status,
                    "priority": priority
                }
            )

            # =============================================
            # ASSIGNEE NODE
            # =============================================

            if assignee:

                owner_id = (
                    f"owner:{assignee}"
                )

                add_node(
                    owner_id,
                    "owner",
                    assignee
                )

                edges.append({
                    "source": issue_key,
                    "target": owner_id,
                    "relationship": "assigned_to"
                })

            # =============================================
            # PROJECT NODE
            # =============================================

            if project:

                project_id = (
                    f"project:{project}"
                )

                add_node(
                    project_id,
                    "service",
                    project
                )

                edges.append({
                    "source": issue_key,
                    "target": project_id,
                    "relationship": "belongs_to"
                })

            # =============================================
            # COMPONENT / SERVICE NODE
            # =============================================

            for component in components:

                component_name = component.get(
                    "name"
                )

                if not component_name:
                    continue

                service_id = (
                    f"service:{component_name}"
                )

                add_node(
                    service_id,
                    "service",
                    component_name
                )

                edges.append({
                    "source": issue_key,
                    "target": service_id,
                    "relationship": "belongs_to"
                })

            # =============================================
            # JIRA ISSUE LINKS
            # =============================================

            issue_links = (
                fields.get("issuelinks") or []
            )

            for link in issue_links:

                link_type = (
                    link.get("type") or {}
                )

                outward_name = link_type.get(
                    "outward",
                    "blocks"
                )

                inward_name = link_type.get(
                    "inward",
                    "blocked_by"
                )

                outward_issue = link.get(
                    "outwardIssue"
                )

                inward_issue = link.get(
                    "inwardIssue"
                )

                # -----------------------------------------
                # CURRENT ISSUE -> OUTWARD ISSUE
                # Example:
                # KAN-1 blocks KAN-2
                # -----------------------------------------

                if outward_issue:

                    target_key = outward_issue.get(
                        "key"
                    )

                    if target_key:

                        add_node(
                            target_key,
                            "workflow",
                            target_key
                        )

                        edges.append({
                            "source": issue_key,
                            "target": target_key,
                            "relationship": outward_name
                        })

                # -----------------------------------------
                # INWARD ISSUE -> CURRENT ISSUE
                # Example:
                # KAN-1 is blocked by KAN-2
                # -----------------------------------------

                if inward_issue:

                    source_key = inward_issue.get(
                        "key"
                    )

                    if source_key:

                        add_node(
                            source_key,
                            "workflow",
                            source_key
                        )

                        edges.append({
                            "source": source_key,
                            "target": issue_key,
                            "relationship": inward_name
                        })

        # =============================================
        # REMOVE DUPLICATE EDGES
        # =============================================

        unique_edges = []
        seen_edges = set()

        for edge in edges:

            edge_key = (
                edge["source"],
                edge["target"],
                edge["relationship"]
            )

            if edge_key in seen_edges:
                continue

            seen_edges.add(
                edge_key
            )

            unique_edges.append(
                edge
            )

        return {
            "nodes": nodes,
            "edges": unique_edges,
            "node_count": len(nodes),
            "edge_count": len(unique_edges)
        }