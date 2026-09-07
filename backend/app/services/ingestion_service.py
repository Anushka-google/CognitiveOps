import logging
import json

from app.services.chunk_service import create_chunks
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

        cleaned_text = CleaningService.clean_text(
            text
        )

        if not cleaned_text:
            return {
                "source": source,
                "source_type": source_type,
                "chunks_ingested": 0
            }

        chunks = create_chunks(
            cleaned_text
        )

        metadata = [
            {
                "source": source,
                "source_type": source_type
            }
            for _ in chunks
        ]

        add_chunks(
            chunks,
            metadata
        )

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

            workflow_data = self._object_to_dict(
                workflow
            )

            cleaned_workflow = (
                CleaningService.clean_workflow(
                    workflow_data
                )
            )

            if not cleaned_workflow:
                continue

            workflow_key = str(
                cleaned_workflow
            ).lower()

            if workflow_key in seen_workflows:
                continue

            seen_workflows.add(
                workflow_key
            )

            cleaned_workflows.append(
                cleaned_workflow
            )

        for workflow_data in cleaned_workflows:

            text = self._workflow_to_text(
                workflow_data
            )

            if not text.strip():
                continue

            chunks = create_chunks(
                text
            )

            for chunk in chunks:

                documents.append(
                    chunk
                )

                metadata.append({
                    "source": source,
                    "source_type": source_type
                })

        if documents:
            add_chunks(
                documents,
                metadata
            )

        logger.info(
            "RAG WORKFLOW INGESTION | source=%s | source_type=%s | records=%s | cleaned_records=%s | chunks=%s",
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

        workflows = (
            jira_service.get_workflow_records()
        )

        result = self.ingest_workflows(
            workflows,
            source="jira",
            source_type="jira_workflow"
        )

        logger.info(
            "RAG JIRA INGESTION COMPLETE | records=%s | chunks=%s",
            result.get(
                "records_ingested",
                0
            ),
            result.get(
                "chunks_ingested",
                0
            )
        )

        return result


    def ingest_slack(
        self,
        limit: int = 100
    ):

        slack_service = SlackService()

        messages = (
            slack_service.get_channel_messages(
                limit=limit
            )
        )

        documents = []
        metadata = []

        seen_messages = set()

        for message in messages:

            if not isinstance(
                message,
                dict
            ):
                continue

            text = CleaningService.clean_text(
                message.get(
                    "text",
                    ""
                )
            )

            if not text:
                continue

            message_key = text.lower()

            if message_key in seen_messages:
                continue

            seen_messages.add(
                message_key
            )

            chunks = create_chunks(
                text
            )

            timestamp = message.get(
                "ts"
            )

            for chunk in chunks:

                documents.append(
                    chunk
                )

                metadata.append({
                    "source": "slack",
                    "source_type": "slack_message",
                    "timestamp": str(
                        timestamp or ""
                    )
                })

        if documents:
            add_chunks(
                documents,
                metadata
            )

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


    def _workflow_to_text(
        self,
        workflow
    ):

        if not isinstance(
            workflow,
            dict
        ):
            workflow = self._object_to_dict(
                workflow
            )

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

            value = workflow.get(
                field
            )

            if value is not None:
                lines.append(
                    f"{field}: {value}"
                )

        if not lines:
            return ""

        return "\n".join(
            lines
        )


    @staticmethod
    def _object_to_dict(
        value
    ):

        if isinstance(
            value,
            dict
        ):
            return value

        if hasattr(
            value,
            "model_dump"
        ):
            return value.model_dump()

        if hasattr(
            value,
            "dict"
        ):
            return value.dict()

        if hasattr(
            value,
            "__dict__"
        ):
            return {
                key: item
                for key, item in vars(
                    value
                ).items()
                if not key.startswith("_")
            }

        try:
            return json.loads(
                json.dumps(
                    value,
                    default=str
                )
            )

        except Exception:
            return {}