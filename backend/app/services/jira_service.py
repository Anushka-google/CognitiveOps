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

    # =========================================================
    # GET JIRA TICKETS
    # =========================================================
    def get_tickets(self):

        url = f"{self.base_url}/rest/api/3/search/jql"

        params = {
            "jql": f"project = {self.project_key}",
            "fields": (
                "summary,"
                "status,"
                "assignee,"
                "created,"
                "updated,"
                "priority,"
                "issuetype,"
                "duedate"
            ),
            "maxResults": 100
        }

        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(
                self.email,
                self.api_token
            ),
            headers={
                "Accept": "application/json"
            },
            timeout=30
        )

        # =====================================================
        # JIRA DEBUG
        # =====================================================

        print("\n==============================================")
        print("              JIRA DEBUG")
        print("==============================================")

        print("BASE URL :", self.base_url)
        print("EMAIL    :", self.email)
        print("PROJECT  :", self.project_key)
        print("REQUEST  :", response.request.url)
        print("STATUS   :", response.status_code)

        print("RESPONSE :")
        print(response.text)

        print("==============================================\n")

        # =====================================================
        # HANDLE ERROR
        # =====================================================

        if response.status_code != 200:

            raise Exception(
                f"Jira API Error {response.status_code}: "
                f"{response.text}"
            )

        # =====================================================
        # PARSE RESPONSE
        # =====================================================

        data = response.json()

        issues = data.get("issues", [])

        print("TOTAL ISSUES :", len(issues))

        return issues

    # =========================================================
    # CONVERT JIRA TICKETS TO WORKFLOW RECORDS
    # =========================================================
    def get_workflow_records(self):

        tickets = self.get_tickets()

        print("TOTAL TICKETS :", len(tickets))

        workflows = []

        for ticket in tickets:

            try:

                workflow = map_jira_to_workflow(ticket)

                workflows.append(workflow)

            except Exception as e:

                print(
                    f"Failed mapping "
                    f"{ticket.get('key')} -> {e}"
                )

        print("TOTAL WORKFLOWS :", len(workflows))

        return workflows

    # =========================================================
    # CHECK JIRA ACCOUNT
    # =========================================================
    def check_identity(self):

        url = f"{self.base_url}/rest/api/3/myself"

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

        print("\n==============================================")
        print("           JIRA IDENTITY CHECK")
        print("==============================================")

        print("STATUS   :", response.status_code)
        print("RESPONSE :")
        print(response.text)

        print("==============================================\n")

        return {
            "status": response.status_code,
            "response": response.json()
        }

    # =========================================================
    # CHECK JIRA PROJECT
    # =========================================================
    def check_project(self):

        url = (
            f"{self.base_url}"
            f"/rest/api/3/project/{self.project_key}"
        )

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

        print("\n==============================================")
        print("             JIRA PROJECT CHECK")
        print("==============================================")

        print("PROJECT  :", self.project_key)
        print("STATUS   :", response.status_code)
        print("RESPONSE :")
        print(response.text)

        print("==============================================\n")

        return {
            "status": response.status_code,
            "response": response.json()
        }