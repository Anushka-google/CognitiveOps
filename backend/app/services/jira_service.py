import os
import requests
from dotenv import load_dotenv

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
            f"/rest/api/3/search/jql"
        )

        params = {
            "jql":
                f"project={self.project_key}",
            "maxResults": 100,
            "fields": "*all"
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

        print("STATUS:",
              response.status_code)

        print("BODY:",
              response.text)

        data = response.json()

        print("TYPE:",
              type(data))

        print("DATA:",
              data)

        return data

    def get_workflow_records(self):

        tickets = self.get_tickets()

        print(
            "TICKETS TYPE:",
            type(tickets)
        )

        print(
            "TICKETS:",
            tickets
        )

        return tickets