# from fastapi import APIRouter
# import os

# # #from app.services.workflow_graph_service import (
# #     WorkflowGraphService
# # )

# # from app.services.jira_service import (
# #     JiraService
# # )

# router = APIRouter()


# @router.get("/jira/test")
# def test_jira():

#     service = JiraService()

#     tickets = service.get_tickets()

#     return tickets[:5]


# @router.post("/workflow/analyze")
# def analyze_workflow():

#     jira_service = JiraService()

#     workflows = (
#         jira_service.get_workflow_records()
#     )

#     service = WorkflowGraphService()

#     result = service.analyze(
#         workflows
#     )

#     return result


# @router.get("/jira/debug")
# def jira_debug():

#     return {
#         "base_url": os.getenv("JIRA_BASE_URL"),
#         "email": os.getenv("JIRA_EMAIL"),
#         "project": os.getenv("JIRA_PROJECT_KEY"),
#         "token_exists": bool(
#             os.getenv("JIRA_API_TOKEN")
#         )
#     }


from fastapi import APIRouter
from app.services.jira_service import JiraService
import os

print("NEW DEPLOY TEST")

router = APIRouter()


@router.get("/jira/debug")
def jira_debug():

    return {
        "base_url": os.getenv(
            "JIRA_BASE_URL"
        ),
        "email": os.getenv(
            "JIRA_EMAIL"
        ),
        "project": os.getenv(
            "JIRA_PROJECT_KEY"
        ),
        "token_exists": bool(
            os.getenv(
                "JIRA_API_TOKEN"
            )
        )
    }



@router.get("/jira/test")
def test_jira():

    try:
        service = JiraService()
        tickets = service.get_tickets()
        return tickets[:5]

    except Exception as e:
        return {
            "error": str(e)
        }