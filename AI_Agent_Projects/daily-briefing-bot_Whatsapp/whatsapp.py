"""
whatsapp.py
-----------
Sends the finished briefing to your own WhatsApp using Twilio's
WhatsApp Sandbox — a free testing number Twilio provides so
individual developers can send WhatsApp messages without needing
a verified business account.

One-time setup required before this works — see README.md.
"""

from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    MY_WHATSAPP_NUMBER,
)


def send_whatsapp_message(message: str) -> str:
    """
    Sends `message` to MY_WHATSAPP_NUMBER via Twilio's WhatsApp Sandbox.
    Returns the message SID (a unique ID Twilio assigns) on success.
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    sent = client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
        to=f"whatsapp:{MY_WHATSAPP_NUMBER}",
        body=message,
    )
    return sent.sid


if __name__ == "__main__":
    sid = send_whatsapp_message("Test message from Daily Briefing Bot!")
    print(f"Sent. Message SID: {sid}")
