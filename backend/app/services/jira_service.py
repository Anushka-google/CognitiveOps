import os
from urllib import response
import requests

from dotenv import load_dotenv

from app.services.workflow_mapper import (
    map_jira_to_workflow
)

load_dotenv()


class JiraService:

    def __init__(self):

        self.base_url = os.getenv(
            "JIRA_BASE_URL"
        )

        self.email = os.getenv(
            "JIRA_EMAIL"
        )

        self.api_token = os.getenv(
            "JIRA_API_TOKEN"
        )

        self.project_key = os.getenv(
            "JIRA_PROJECT_KEY"
        )

    def get_tickets(self):

        url = (
            f"{self.base_url}"
            f"/rest/api/3/search"
        )

        params = {
            "jql":
                f"project={self.project_key}",
            "maxResults": 100
        }

        response = requests.get(
            url,
            params=params,
            auth=(
                self.email,
                self.api_token
            ),
            headers={
                "Accept":
                "application/json"
            }
        )

        print(response.status_code)
        print(response.text)

        response.raise_for_status()

        response.raise_for_status()

        data = response.json()

        return data.get(
            "issues",
            []
        )

    def get_workflow_records(self):

        tickets = (
            self.get_tickets()
        )

        workflows = [
            map_jira_to_workflow(
                ticket
            )
            for ticket in tickets
        ]

        return workflows