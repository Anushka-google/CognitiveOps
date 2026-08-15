import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

from app.services.workflow_mapper import map_jira_to_workflow

load_dotenv()


class JiraService:

    def __init__(self):

        self.base_url = os.getenv("JIRA_BASE_URL", "").strip()
        self.email = os.getenv("JIRA_EMAIL", "").strip()
        self.api_token = os.getenv("JIRA_API_TOKEN", "").strip()
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "").strip()

    # ---------------------------------------------------------
    # GET JIRA TICKETS
    # ---------------------------------------------------------
    def get_tickets(self):

        url = f"{self.base_url}/rest/api/3/search/jql"

        payload = {
            "jql": f'project = "{self.project_key}"',
            "fields": [
                "summary",
                "status",
                "assignee",
                "created",
                "updated",
                "priority",
                "issuetype",
                "duedate"
            ],
            "maxResults": 100
        }

        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(
                self.email,
                self.api_token
            ),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        print("\n========== JIRA DEBUG ==========")
        print("BASE URL:", self.base_url)
        print("EMAIL:", self.email)
        print("PROJECT:", self.project_key)
        print("TOKEN EXISTS:", bool(self.api_token))
        print("REQUEST URL:", response.request.url)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("================================")

        response.raise_for_status()

        data = response.json()

        issues = data.get("issues", [])

        print("TOTAL ISSUES:", len(issues))

        return issues

    # ---------------------------------------------------------
    # GET JIRA PROJECT DIRECTLY
    # ---------------------------------------------------------
    def check_project(self):

        url = f"{self.base_url}/rest/api/3/project/{self.project_key}"

        response = requests.get(
            url,
            auth=HTTPBasicAuth(
                self.email,
                self.api_token
            ),
            headers={
                "Accept": "application/json"
            },
            timeout=30
        )

        return {
            "status": response.status_code,
            "response": response.text
        }

    # ---------------------------------------------------------
    # MAP JIRA → WORKFLOW
    # ---------------------------------------------------------
    def get_workflow_records(self):

        tickets = self.get_tickets()

        print("TOTAL TICKETS:", len(tickets))

        workflows = []

        for ticket in tickets:

            try:

                workflow = map_jira_to_workflow(ticket)

                workflows.append(workflow)

            except Exception as e:

                print(
                    f"FAILED MAPPING {ticket.get('key')} -> {e}"
                )

        print("TOTAL WORKFLOWS:", len(workflows))

        return workflows