import os
import requests

from requests.auth import (
    HTTPBasicAuth
)

from dotenv import (
    load_dotenv
)

from app.services.workflow_mapper import (
    map_jira_to_workflow
)


load_dotenv()


class JiraService:

    def __init__(self):

        self.base_url = (
            os.getenv(
                "JIRA_BASE_URL",
                ""
            )
            .strip()
            .rstrip("/")
        )

        self.email = (
            os.getenv(
                "JIRA_EMAIL",
                ""
            )
            .strip()
        )

        self.api_token = (
            os.getenv(
                "JIRA_API_TOKEN",
                ""
            )
            .strip()
        )

        self.project_key = (
            os.getenv(
                "JIRA_PROJECT_KEY",
                ""
            )
            .strip()
        )

        self.auth = HTTPBasicAuth(
            self.email,
            self.api_token
        )

        self.headers = {

            "Accept":
                "application/json",

            "Content-Type":
                "application/json"
        }

    # =========================================================
    # BASIC CONFIG CHECK
    # =========================================================

    def check_config(self):

        return {

            "base_url_exists":
                bool(self.base_url),

            "email_exists":
                bool(self.email),

            "token_exists":
                bool(self.api_token),

            "project_key":
                self.project_key
        }

    # =========================================================
    # CHECK JIRA ACCOUNT
    # =========================================================

    def check_identity(self):

        url = (
            f"{self.base_url}"
            f"/rest/api/3/myself"
        )

        response = requests.get(
            url,
            auth=self.auth,
            headers=self.headers,
            timeout=30
        )

        print(
            "\n=============================================="
        )

        print(
            "             JIRA IDENTITY CHECK"
        )

        print(
            "=============================================="
        )

        print(
            "URL    :",
            url
        )

        print(
            "STATUS :",
            response.status_code
        )

        print(
            "BODY   :",
            response.text
        )

        print(
            "==============================================\n"
        )

        try:

            data = response.json()

        except Exception:

            data = {

                "raw_response":
                    response.text
            }

        return {

            "status":
                response.status_code,

            "response":
                data
        }

    # =========================================================
    # CHECK PROJECT
    # =========================================================

    def check_project(self):

        url = (
            f"{self.base_url}"
            f"/rest/api/3/project/"
            f"{self.project_key}"
        )

        response = requests.get(
            url,
            auth=self.auth,
            headers=self.headers,
            timeout=30
        )

        print(
            "\n=============================================="
        )

        print(
            "              JIRA PROJECT CHECK"
        )

        print(
            "=============================================="
        )

        print(
            "PROJECT :",
            self.project_key
        )

        print(
            "URL     :",
            url
        )

        print(
            "STATUS  :",
            response.status_code
        )

        print(
            "BODY    :",
            response.text
        )

        print(
            "==============================================\n"
        )

        try:

            data = response.json()

        except Exception:

            data = {

                "raw_response":
                    response.text
            }

        return {

            "status":
                response.status_code,

            "response":
                data
        }

    # =========================================================
    # CHECK BROWSE PROJECT PERMISSION
    # =========================================================

    def check_permissions(self):

        url = (
            f"{self.base_url}"
            f"/rest/api/3/mypermissions"
        )

        params = {

            "projectKey":
                self.project_key,

            "permissions":
                "BROWSE_PROJECTS,VIEW_ISSUES"
        }

        response = requests.get(
            url,
            params=params,
            auth=self.auth,
            headers=self.headers,
            timeout=30
        )

        print(
            "\n=============================================="
        )

        print(
            "             JIRA PERMISSION CHECK"
        )

        print(
            "=============================================="
        )

        print(
            "PROJECT :",
            self.project_key
        )

        print(
            "URL     :",
            response.request.url
        )

        print(
            "STATUS  :",
            response.status_code
        )

        print(
            "BODY    :",
            response.text
        )

        print(
            "==============================================\n"
        )

        try:

            data = response.json()

        except Exception:

            data = {

                "raw_response":
                    response.text
            }

        return {

            "status":
                response.status_code,

            "response":
                data
        }

    # =========================================================
    # GET ACCESSIBLE PROJECTS
    # =========================================================

    def get_accessible_projects(self):

        url = (
            f"{self.base_url}"
            f"/rest/api/3/project/search"
        )

        params = {

            "keys":
                self.project_key,

            "maxResults":
                50
        }

        response = requests.get(
            url,
            params=params,
            auth=self.auth,
            headers=self.headers,
            timeout=30
        )

        print(
            "\n=============================================="
        )

        print(
            "          ACCESSIBLE PROJECT CHECK"
        )

        print(
            "=============================================="
        )

        print(
            "PROJECT :",
            self.project_key
        )

        print(
            "URL     :",
            response.request.url
        )

        print(
            "STATUS  :",
            response.status_code
        )

        print(
            "BODY    :",
            response.text
        )

        print(
            "==============================================\n"
        )

        try:

            data = response.json()

        except Exception:

            data = {

                "raw_response":
                    response.text
            }

        return {

            "status":
                response.status_code,

            "response":
                data
        }

    # =========================================================
    # GET JIRA TICKETS
    # =========================================================

    def get_tickets(self):

        if not self.base_url:

            raise Exception(
                "JIRA_BASE_URL is missing"
            )

        if not self.email:

            raise Exception(
                "JIRA_EMAIL is missing"
            )

        if not self.api_token:

            raise Exception(
                "JIRA_API_TOKEN is missing"
            )

        if not self.project_key:

            raise Exception(
                "JIRA_PROJECT_KEY is missing"
            )

        url = (
            f"{self.base_url}"
            f"/rest/api/3/search/jql"
        )

        params = {

            "jql":
                f'project = "{self.project_key}"',

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

            "maxResults":
                100
        }

        response = requests.get(
            url,
            params=params,
            auth=self.auth,
            headers=self.headers,
            timeout=30
        )

        print(
            "\n=============================================="
        )

        print(
            "                JIRA SEARCH"
        )

        print(
            "=============================================="
        )

        print(
            "BASE URL :",
            self.base_url
        )

        print(
            "EMAIL    :",
            self.email
        )

        print(
            "PROJECT  :",
            self.project_key
        )

        print(
            "REQUEST  :",
            response.request.url
        )

        print(
            "STATUS   :",
            response.status_code
        )

        print(
            "RESPONSE :"
        )

        print(
            response.text
        )

        print(
            "==============================================\n"
        )

        if response.status_code != 200:

            raise Exception(
                f"Jira API Error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        issues = data.get(
            "issues",
            []
        )

        print(
            "TOTAL ISSUES :",
            len(issues)
        )

        return issues

    # =========================================================
    # CONVERT JIRA TICKETS TO WORKFLOW RECORDS
    # =========================================================

    def get_workflow_records(self):

        tickets = self.get_tickets()

        print(
            "TOTAL TICKETS :",
            len(tickets)
        )

        workflows = []

        for ticket in tickets:

            try:

                workflow = (
                    map_jira_to_workflow(
                        ticket
                    )
                )

                workflows.append(
                    workflow
                )

            except Exception as e:

                print(
                    f"Failed mapping "
                    f"{ticket.get('key')} -> {e}"
                )

        print(
            "TOTAL WORKFLOWS :",
            len(workflows)
        )

        return workflows

    # =========================================================
    # HUMAN-IN-THE-LOOP ACTION
    #
    # This method is ONLY called after human approval.
    # =========================================================

    def update_issue_priority(
        self,
        issue_key,
        priority_name="Highest"
    ):

        if not issue_key:

            raise Exception(
                "Jira issue key is required"
            )

        if not self.base_url:

            raise Exception(
                "JIRA_BASE_URL is missing"
            )

        if not self.email:

            raise Exception(
                "JIRA_EMAIL is missing"
            )

        if not self.api_token:

            raise Exception(
                "JIRA_API_TOKEN is missing"
            )

        url = (
            f"{self.base_url}"
            f"/rest/api/3/issue/"
            f"{issue_key}"
        )

        payload = {

            "fields": {

                "priority": {

                    "name":
                        priority_name
                }
            }
        }

        print(
            "\n=============================================="
        )

        print(
            "        APPROVED JIRA ACTION"
        )

        print(
            "=============================================="
        )

        print(
            "ISSUE    :",
            issue_key
        )

        print(
            "PRIORITY :",
            priority_name
        )

        print(
            "URL      :",
            url
        )

        print(
            "==============================================\n"
        )

        response = requests.put(
            url,
            json=payload,
            auth=self.auth,
            headers=self.headers,
            timeout=30
        )

        if response.status_code not in (
            200,
            204
        ):

            raise Exception(
                f"Jira update failed "
                f"{response.status_code}: "
                f"{response.text}"
            )

        try:

            response_data = (
                response.json()
                if response.text
                else {}
            )

        except Exception:

            response_data = {

                "raw_response":
                    response.text
            }

        return {

            "status":
                response.status_code,

            "issue_key":
                issue_key,

            "field":
                "priority",

            "new_value":
                priority_name,

            "response":
                response_data
        }