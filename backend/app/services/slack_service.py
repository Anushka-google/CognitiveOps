import os
import logging
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SlackService:
    """
    Enterprise Slack Integration Service.
    Supports:
    1. Incident Alerting via Incoming Webhook (formatted Block Kit messages).
    2. Operational Ticket & Blocker Notifications.
    3. Channel History Reading via Slack Web API (evidence harvesting for RAG).
    4. Two-way Ticket Evidence Association.
    """

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
        self.bot_token = os.getenv("SLACK_BOT_TOKEN", "").strip()
        self.channel_id = os.getenv("SLACK_CHANNEL_ID", "").strip()

    def get_status(self) -> Dict[str, Any]:
        """Returns the health and connection status of the Slack integration."""
        return {
            "configured": bool(self.webhook_url or self.bot_token),
            "has_webhook": bool(self.webhook_url),
            "has_bot_token": bool(self.bot_token),
            "channel_id": self.channel_id or "default"
        }

    def send_alert(self, message: str) -> int:
        """Sends a simple text alert to Slack webhook."""
        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL is not set. Simulating alert.")
            return 200

        payload = {"text": message}
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            logger.info("SLACK ALERT STATUS: %s", response.status_code)
            return response.status_code
        except Exception as e:
            logger.error("Failed to post message to Slack: %s", e)
            return 500

    def send_incident_card(
        self,
        ticket_id: str,
        title: str,
        status: str,
        priority: str,
        impact_summary: str,
        action_required: str = "Investigation Required"
    ) -> Dict[str, Any]:
        """
        Sends an executive Slack Block Kit card alerting DevOps/Engineering leads
        about an SLA risk, bottleneck, or blocker.
        """
        color = "#E01E5A" if priority.lower() in ["critical", "high"] else "#ECB22E"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 CognitiveOps Incident Alert: {ticket_id}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Title:*\n{title}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{status}"},
                    {"type": "mrkdwn", "text": f"*Priority:*\n{priority}"},
                    {"type": "mrkdwn", "text": f"*Action:*\n{action_required}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*AI Diagnosis & Impact:*\n{impact_summary}"
                }
            },
            {
                "type": "divider"
            }
        ]

        payload = {
            "attachments": [
                {
                    "color": color,
                    "blocks": blocks
                }
            ]
        }

        if not self.webhook_url:
            logger.info("Slack webhook simulated successfully for ticket %s", ticket_id)
            return {"status": "simulated", "delivered": True, "ticket_id": ticket_id}

        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            return {
                "status": "delivered" if resp.status_code == 200 else "failed",
                "status_code": resp.status_code,
                "ticket_id": ticket_id
            }
        except Exception as e:
            logger.error("Failed to send Slack incident card: %s", e)
            return {"status": "error", "message": str(e), "ticket_id": ticket_id}

    def get_channel_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Reads conversational history from the Slack channel for RAG indexing."""
        if not self.bot_token or not self.channel_id:
            # Fallback mock evidence so local and offline demos work seamlessly
            return [
                {
                    "text": "KAN-101 deployment is blocked because approval is pending in release pipeline.",
                    "ts": "1725700000.000100",
                    "user": "U123456"
                },
                {
                    "text": "OPS-201 database migration is blocked by staging infra timeouts. Investigating.",
                    "ts": "1725700500.000200",
                    "user": "U789012"
                },
                {
                    "text": "KAN-103 blocker resolved, frontend tests passing now.",
                    "ts": "1725701000.000300",
                    "user": "U345678"
                }
            ]

        url = "https://slack.com/api/conversations.history"
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        params = {"channel": self.channel_id, "limit": limit}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            data = response.json()
            if not data.get("ok"):
                logger.warning("Slack API Error: %s", data.get("error"))
                return []
            return data.get("messages", [])
        except Exception as e:
            logger.error("Failed to query Slack API history: %s", e)
            return []

    def get_ticket_evidence(self, ticket_id: str) -> List[Dict[str, Any]]:
        """Extracts Slack messages mentioning a specific ticket."""
        messages = self.get_channel_messages()
        evidence = []
        ticket_id = str(ticket_id).strip().upper()

        for message in messages:
            text = str(message.get("text", ""))
            if ticket_id in text.upper():
                evidence.append({
                    "ticket_id": ticket_id,
                    "message": text,
                    "timestamp": message.get("ts"),
                    "source": "slack"
                })

        return evidence