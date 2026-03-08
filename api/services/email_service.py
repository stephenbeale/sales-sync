"""Gmail API integration for monitoring Vinted sale notifications."""

import base64
import logging
import os
import re
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GMAIL_CREDENTIALS_FILE, GMAIL_TOKEN_FILE, VINTED_SENDER

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """Authenticate and return a Gmail API service instance."""
    creds = None

    if os.path.exists(GMAIL_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(GMAIL_CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Gmail credentials file not found: {GMAIL_CREDENTIALS_FILE}. "
                    "Download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(GMAIL_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def check_for_sales(after_timestamp=None):
    """Check Gmail for Vinted sale notification emails.

    Args:
        after_timestamp: ISO timestamp - only return emails after this time.

    Returns:
        List of dicts with parsed sale info: {subject, item_title, received_at, message_id}
    """
    try:
        service = get_gmail_service()

        query = f"from:{VINTED_SENDER} subject:sold"
        if after_timestamp:
            dt = datetime.fromisoformat(after_timestamp)
            query += f" after:{int(dt.timestamp())}"

        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=10)
            .execute()
        )

        messages = results.get("messages", [])
        sales = []

        for msg_ref in messages:
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=msg_ref["id"], format="full")
                .execute()
            )

            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
            subject = headers.get("Subject", "")
            received_at = headers.get("Date", "")

            item_title = parse_item_title(subject, msg)

            if item_title:
                sales.append(
                    {
                        "subject": subject,
                        "item_title": item_title,
                        "received_at": received_at,
                        "message_id": msg_ref["id"],
                    }
                )

        return sales

    except FileNotFoundError:
        logger.warning("Gmail credentials not set up yet")
        return []
    except Exception as e:
        logger.error("Failed to check Gmail: %s", e)
        return []


def parse_item_title(subject, message):
    """Extract the sold item title from a Vinted notification.

    This will need adjusting based on the actual email format.
    Common patterns: "You sold [Item Name]!", "Your item has been sold: Item Name"
    """
    # Try subject line patterns
    patterns = [
        r"You sold (.+?)!",
        r"sold: (.+?)$",
        r"Your item (.+?) has been sold",
        r"Congratulations! (.+?) has been sold",
    ]

    for pattern in patterns:
        match = re.search(pattern, subject, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Try email body as fallback
    body = get_message_body(message)
    if body:
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1).strip()

    # Fall back to subject with common prefixes removed
    cleaned = re.sub(
        r"^(Re:\s*|Fwd:\s*|Vinted:\s*)", "", subject, flags=re.IGNORECASE
    ).strip()
    return cleaned if cleaned else None


def get_message_body(message):
    """Extract plain text body from a Gmail message."""
    payload = message.get("payload", {})

    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    return None
