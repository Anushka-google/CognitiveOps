import os
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

        print(
            "SLACK STATUS:",
            response.status_code
        )

        print(
            "SLACK RESPONSE:",
            response.text
        )

        return response.status_code


    def get_channel_messages(
        self,
        limit=100
    ):

        token = os.getenv(
            "SLACK_BOT_TOKEN"
        )

        channel_id = os.getenv(
            "SLACK_CHANNEL_ID"
        )

        url = (
            "https://slack.com/api/"
            "conversations.history"
        )

        headers = {
            "Authorization": f"Bearer {token}"
        }

        params = {
            "channel": channel_id,
            "limit": limit
        }

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        data = response.json()

        print(
            "SLACK HISTORY STATUS:",
            response.status_code
        )

        print(
            "SLACK HISTORY RESPONSE:",
            data
        )

        if not data.get("ok"):
            print(
                "SLACK API ERROR:",
                data.get("error")
            )

            return []

        return data.get(
            "messages",
            []
        )


    def get_ticket_evidence(
        self,
        ticket_id
    ):

        messages = self.get_channel_messages()

        evidence = []

        ticket_id = str(
            ticket_id
        ).strip().upper()

        for message in messages:

            text = str(
                message.get(
                    "text",
                    ""
                )
            )

            if ticket_id in text.upper():

                evidence.append({
                    "ticket_id": ticket_id,
                    "message": text,
                    "timestamp": message.get(
                        "ts"
                    )
                })

        print(
            "SLACK TICKET EVIDENCE | %s | count=%s",
            ticket_id,
            len(evidence)
        )

        return evidence