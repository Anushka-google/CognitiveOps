import re


class CleaningService:

    @staticmethod
    def clean_text(text):
        """
        Clean raw text before chunking and ingestion.
        """

        if text is None:
            return ""

        if not isinstance(text, str):
            text = str(text)

        text = text.strip()

        if not text:
            return ""

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove obvious control characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        text = text.strip()

        # Filter obvious noise
        if CleaningService.is_noise(text):
            return ""

        return text

    @staticmethod
    def is_noise(text):
        """
        Detect obviously useless content.

        This intentionally uses conservative rules so that
        meaningful short workflow content is not removed.
        """

        if not text:
            return True

        normalized = text.strip()

        if not normalized:
            return True

        # Only punctuation/symbols
        if not re.search(r"[A-Za-z0-9]", normalized):
            return True

        # Common meaningless placeholders
        noise_values = {
            "n/a",
            "na",
            "none",
            "null",
            "undefined",
            "test",
            "testing"
        }

        if normalized.lower() in noise_values:
            return True

        return False

    @staticmethod
    def remove_duplicates(items):
        """
        Remove duplicate strings while preserving order.
        """

        unique_items = []
        seen = set()

        for item in items:

            cleaned = CleaningService.clean_text(item)

            if not cleaned:
                continue

            key = cleaned.lower()

            if key in seen:
                continue

            seen.add(key)
            unique_items.append(cleaned)

        return unique_items

    @staticmethod
    def clean_workflow(workflow):
        """
        Clean a workflow record.

        Invalid/non-dictionary records are ignored.
        Empty field values are removed.
        """

        if workflow is None:
            return None

        if not isinstance(workflow, dict):
            if hasattr(workflow, "model_dump"):
                workflow = workflow.model_dump()

            elif hasattr(workflow, "dict"):
                workflow = workflow.dict()

            else:
                return None

        cleaned = {}

        for key, value in workflow.items():

            if value is None:
                continue

            if isinstance(value, str):

                value = CleaningService.clean_text(value)

                if not value:
                    continue

            cleaned[key] = value

        if not cleaned:
            return None

        return cleaned