import pytest


@pytest.fixture
def sample_issue_key():
    return "KAN-2"


@pytest.fixture
def sample_priority():
    return "Highest"


@pytest.fixture
def sample_proposed_action(
    sample_issue_key,
    sample_priority
):
    return {
        "action_type": "jira_update_priority",
        "target": sample_issue_key,
        "field": "priority",
        "new_value": sample_priority,
        "description": (
            f"Update Jira issue "
            f"{sample_issue_key} "
            f"priority to "
            f"{sample_priority}."
        ),
        "impact_level": "high",
        "requires_human_approval": True
    }