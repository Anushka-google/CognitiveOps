import re


def create_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Generic character-based chunking.

    Kept for backward compatibility and generic documents.
    """

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(
                chunk.strip()
            )

        start += (
            chunk_size - overlap
        )

    return chunks


def create_document_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Paragraph-aware chunking for normal documents/text.

    Attempts to keep paragraphs together before falling back
    to generic character chunking for very large paragraphs.
    """

    if not text or not text.strip():
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n",
            text
        )
        if paragraph.strip()
    ]

    if not paragraphs:
        return []

    chunks = []
    current = ""

    for paragraph in paragraphs:

        if not current:
            current = paragraph
            continue

        candidate = (
            current
            + "\n\n"
            + paragraph
        )

        if len(candidate) <= chunk_size:
            current = candidate

        else:
            chunks.append(
                current.strip()
            )

            current = paragraph

    if current:
        chunks.append(
            current.strip()
        )

    final_chunks = []

    for chunk in chunks:

        if len(chunk) <= chunk_size:
            final_chunks.append(
                chunk
            )

        else:
            final_chunks.extend(
                create_chunks(
                    chunk,
                    chunk_size,
                    overlap
                )
            )

    return final_chunks


def create_slack_chunks(
    message: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Message-aware chunking for Slack.

    A Slack message is treated as one semantic unit whenever
    it fits within the chunk size.
    """

    if not message or not str(message).strip():
        return []

    message = str(message).strip()

    if len(message) <= chunk_size:
        return [message]

    return create_chunks(
        message,
        chunk_size,
        overlap
    )


def create_jira_chunks(
    issue_text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Field-aware chunking for Jira issues.

    Keeps Jira fields together where possible instead of
    blindly splitting characters.
    """

    if not issue_text or not issue_text.strip():
        return []

    lines = [
        line.strip()
        for line in issue_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return []

    chunks = []
    current_lines = []
    current_length = 0

    for line in lines:

        line_length = len(line)

        separator_length = (
            1
            if current_lines
            else 0
        )

        if (
            current_lines
            and
            current_length
            + separator_length
            + line_length
            > chunk_size
        ):

            chunks.append(
                "\n".join(
                    current_lines
                ).strip()
            )

            current_lines = [
                line
            ]

            current_length = (
                line_length
            )

        else:

            current_lines.append(
                line
            )

            current_length += (
                separator_length
                + line_length
            )

    if current_lines:
        chunks.append(
            "\n".join(
                current_lines
            ).strip()
        )

    final_chunks = []

    for chunk in chunks:

        if len(chunk) <= chunk_size:
            final_chunks.append(
                chunk
            )

        else:
            final_chunks.extend(
                create_chunks(
                    chunk,
                    chunk_size,
                    overlap
                )
            )

    return final_chunks


def create_workflow_chunks(
    workflow_text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Record-aware chunking for workflow records.

    A workflow record remains a semantic unit whenever it
    fits within the chunk size.
    """

    if not workflow_text:
        return []

    workflow_text = (
        str(workflow_text)
        .strip()
    )

    if not workflow_text:
        return []

    if len(workflow_text) <= chunk_size:
        return [workflow_text]

    return create_jira_chunks(
        workflow_text,
        chunk_size,
        overlap
    )