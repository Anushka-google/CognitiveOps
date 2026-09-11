import logging
import json
import re

from app.services.chunk_service import (
    create_document_chunks,
    create_slack_chunks,
    create_workflow_chunks
)
from app.services.vector_store import add_chunks
from app.services.jira_service import JiraService
from app.services.slack_service import SlackService
from app.services.cleaning_service import CleaningService


logger = logging.getLogger(__name__)


class IngestionService:

    def ingest_text(
        self,
        text: str,
        source: str = "document",
        source_type: str = "text"
    ):
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")

        cleaned_text = CleaningService.clean_text(text)

        if not cleaned_text:
            return {
                "source": source,
                "source_type": source_type,
                "chunks_ingested": 0
            }

        chunks = create_document_chunks(cleaned_text)

        metadata = [
            self._build_metadata(
                source=source,
                source_type=source_type
            )
            for _ in chunks
        ]

        add_chunks(chunks, metadata)

        logger.info(
            "RAG INGESTION | source=%s | source_type=%s | chunks=%s",
            source,
            source_type,
            len(chunks)
        )

        return {
            "source": source,
            "source_type": source_type,
            "chunks_ingested": len(chunks)
        }

    def ingest_workflows(
        self,
        workflows,
        source: str = "workflow",
        source_type: str = "workflow_record"
    ):
        if not workflows:
            return {
                "source": source,
                "source_type": source_type,
                "records_ingested": 0,
                "chunks_ingested": 0
            }

        documents = []
        metadata = []

        cleaned_workflows = []
        seen_workflows = set()

        for workflow in workflows:
            workflow_data = self._object_to_dict(workflow)
            cleaned_workflow = CleaningService.clean_workflow(
                workflow_data
            )

            if not cleaned_workflow:
                continue

            workflow_key = str(cleaned_workflow).lower()

            if workflow_key in seen_workflows:
                continue

            seen_workflows.add(workflow_key)
            cleaned_workflows.append(cleaned_workflow)

        for workflow_data in cleaned_workflows:
            text = self._workflow_to_text(workflow_data)

            if not text.strip():
                continue

            chunks = create_workflow_chunks(text)

            for chunk in chunks:
                documents.append(chunk)

                metadata.append(
                    self._build_workflow_metadata(
                        workflow_data,
                        source=source,
                        source_type=source_type
                    )
                )

        if documents:
            add_chunks(documents, metadata)

        logger.info(
            "RAG WORKFLOW INGESTION | source=%s | "
            "source_type=%s | records=%s | "
            "cleaned_records=%s | chunks=%s",
            source,
            source_type,
            len(workflows),
            len(cleaned_workflows),
            len(documents)
        )

        return {
            "source": source,
            "source_type": source_type,
            "records_ingested": len(cleaned_workflows),
            "chunks_ingested": len(documents)
        }

    def ingest_jira(self):
        jira_service = JiraService()
        workflows = jira_service.get_workflow_records()

        result = self.ingest_workflows(
            workflows,
            source="jira",
            source_type="jira_workflow"
        )

        logger.info(
            "RAG JIRA INGESTION COMPLETE | records=%s | chunks=%s",
            result.get("records_ingested", 0),
            result.get("chunks_ingested", 0)
        )

        return result

    def ingest_slack(self, limit: int = 100):
        slack_service = SlackService()
        messages = slack_service.get_channel_messages(
            limit=limit
        )

        documents = []
        metadata = []
        seen_messages = set()

        for message in messages:
            if not isinstance(message, dict):
                continue

            text = CleaningService.clean_text(
                message.get("text", "")
            )

            if not text:
                continue

            message_key = text.lower()

            if message_key in seen_messages:
                continue

            seen_messages.add(message_key)

            chunks = create_slack_chunks(text)
            timestamp = message.get("ts")

            for chunk in chunks:
                documents.append(chunk)

                metadata.append(
                    self._build_slack_metadata(
                        message,
                        text,
                        timestamp
                    )
                )

        if documents:
            add_chunks(documents, metadata)

        logger.info(
            "RAG SLACK INGESTION | messages=%s | chunks=%s",
            len(messages),
            len(documents)
        )

        return {
            "source": "slack",
            "source_type": "slack_message",
            "messages_read": len(messages),
            "chunks_ingested": len(documents)
        }

    def _build_metadata(
        self,
        source,
        source_type,
        timestamp="",
        project="",
        issue_id="",
        author="",
        team="",
        priority=""
    ):
        return {
            "source": str(source or ""),
            "source_type": str(source_type or ""),
            "timestamp": str(timestamp or ""),
            "project": str(project or ""),
            "issue_id": str(issue_id or ""),
            "author": str(author or ""),
            "team": str(team or ""),
            "priority": str(priority or "")
        }

    def _build_workflow_metadata(
        self,
        workflow,
        source,
        source_type
    ):
        issue_id = workflow.get("ticket_id", "")

        project = self._extract_project(issue_id)

        timestamp = (
            workflow.get("updated_at")
            or workflow.get("created_at")
            or ""
        )

        author = (
            workflow.get("author")
            or workflow.get("reporter")
            or workflow.get("assignee")
            or ""
        )

        team = workflow.get("team", "")

        priority = workflow.get("priority", "")

        return self._build_metadata(
            source=source,
            source_type=source_type,
            timestamp=timestamp,
            project=project,
            issue_id=issue_id,
            author=author,
            team=team,
            priority=priority
        )

    def _build_slack_metadata(
        self,
        message,
        text,
        timestamp
    ):
        issue_id = self._extract_issue_id(text)

        project = self._extract_project(issue_id)

        author = (
            message.get("author")
            or message.get("username")
            or message.get("user")
            or ""
        )

        team = message.get("team", "")

        priority = message.get("priority", "")

        return self._build_metadata(
            source="slack",
            source_type="slack_message",
            timestamp=timestamp,
            project=project,
            issue_id=issue_id,
            author=author,
            team=team,
            priority=priority
        )

    @staticmethod
    def _extract_issue_id(text):
        if not text:
            return ""

        match = re.search(
            r"\b([A-Z][A-Z0-9]+-\d+)\b",
            str(text).upper()
        )

        if match:
            return match.group(1)

        return ""

    @staticmethod
    def _extract_project(issue_id):
        if not issue_id:
            return ""

        issue_id = str(issue_id).strip().upper()

        if "-" not in issue_id:
            return ""

        return issue_id.split("-", 1)[0]

    def _workflow_to_text(self, workflow):
        if not isinstance(workflow, dict):
            workflow = self._object_to_dict(workflow)

        lines = []

        field_order = [
            "ticket_id",
            "title",
            "status",
            "priority",
            "assignee",
            "due_date",
            "created_at",
            "days_waiting"
        ]

        for field in field_order:
            value = workflow.get(field)

            if value is not None:
                lines.append(
                    f"{field}: {value}"
                )

        if not lines:
            return ""

        return "\n".join(lines)

    @staticmethod
    def _object_to_dict(value):
        if isinstance(value, dict):
            return value

        if hasattr(value, "model_dump"):
            return value.model_dump()

        if hasattr(value, "dict"):
            return value.dict()

        if hasattr(value, "__dict__"):
            return {
                key: item
                for key, item in vars(value).items()
                if not key.startswith("_")
            }

        try:
            return json.loads(
                json.dumps(value, default=str)
            )
        except Exception:
            return {}