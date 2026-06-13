import requests

from app.services.workflow_mapper import map_jira_to_workflow


class JiraService:

    def get_tickets(self):

        response = requests.get(
            "https://jsonplaceholder.typicode.com/posts"
        )

        return response.json()
    
    def get_workflow_records(self):

        tickets = self.get_tickets()

        workflows = [
            map_jira_to_workflow(ticket)
            for ticket in tickets[:2]
        ]

        return workflows