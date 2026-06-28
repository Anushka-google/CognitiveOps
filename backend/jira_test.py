import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("JIRA_BASE_URL").strip() + "/rest/api/3/myself"

r = requests.get(
    url,
    auth=HTTPBasicAuth(
        os.getenv("JIRA_EMAIL").strip(),
        os.getenv("JIRA_API_TOKEN").strip()
    ),
    headers={
        "Accept": "application/json"
    }
)

print("STATUS :", r.status_code)
print("HEADERS :", r.headers.get("content-type"))
print("BODY :")
print(r.text)