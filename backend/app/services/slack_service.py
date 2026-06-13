import os
from urllib import response
import requests

from dotenv import load_dotenv

load_dotenv()


class SlackService:

    def send_alert(
        self,
        message
    ):

        webhook_url = os.getenv(
            "SLACK_WEBHOOK_URL"
        )

        payload = {
            "text": message
        }

        response = requests.post(
            webhook_url,
            json=payload
        )

        print("SLACK STATUS:", response.status_code)
        print("SLACK RESPONSE:", response.text)


        return response.status_code