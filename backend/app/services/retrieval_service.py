from app.services.vector_store import search_chunks


class RetrievalService:

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filters=None,
        distance_threshold: float = 1.5,
        min_evidence: int = 1
    ):
        if not query or not query.strip():
            return self._empty_response(
                reason="empty_query"
            )

        results = search_chunks(
            query=query,
            n_results=n_results,
            filters=filters
        )

        documents = (
            results.get("documents", [[]])[0]
            if results.get("documents")
            else []
        )

        metadatas = (
            results.get("metadatas", [[]])[0]
            if results.get("metadatas")
            else []
        )

        distances = (
            results.get("distances", [[]])[0]
            if results.get("distances")
            else []
        )

        if not documents:
            return self._empty_response(
                reason="no_evidence"
            )

        evidence = []

        for index, document in enumerate(documents):

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            if (
                distance is not None
                and distance > distance_threshold
            ):
                continue

            evidence.append({
                "document": document,
                "metadata": metadata,
                "distance": distance
            })

        if not evidence:
            return {
                "status": "insufficient_evidence",
                "reason": "low_relevance",
                "evidence_count": 0,
                "conflict_detected": False,
                "results": []
            }

        conflict_detected = self._detect_conflicts(
            evidence
        )

        if len(evidence) < min_evidence:
            status = "insufficient_evidence"
        elif conflict_detected:
            status = "conflicting_evidence"
        else:
            status = "reliable"

        return {
            "status": status,
            "reason": (
                "conflicting_evidence"
                if conflict_detected
                else None
            ),
            "evidence_count": len(evidence),
            "conflict_detected": conflict_detected,
            "results": evidence
        }

    def _detect_conflicts(self, evidence):
        issue_statuses = {}

        for item in evidence:
            metadata = item.get("metadata", {})
            document = item.get("document", "")

            issue_id = metadata.get("issue_id")

            if not issue_id:
                continue

            status = self._extract_status(
                document
            )

            if not status:
                continue

            issue_id = str(issue_id).upper()

            if issue_id not in issue_statuses:
                issue_statuses[issue_id] = set()

            issue_statuses[issue_id].add(
                status.lower()
            )

        for statuses in issue_statuses.values():
            if len(statuses) > 1:
                return True

        return False

    @staticmethod
    def _extract_status(document):
        if not document:
            return ""

        for line in str(document).splitlines():

            if ":" not in line:
                continue

            field, value = line.split(
                ":",
                1
            )

            if field.strip().lower() == "status":
                return value.strip()

        return ""

    @staticmethod
    def _empty_response(reason):
        return {
            "status": "no_evidence",
            "reason": reason,
            "evidence_count": 0,
            "conflict_detected": False,
            "results": []
        }