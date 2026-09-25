"""
whatsapp.py
-----------
Sends the finished briefing to your own WhatsApp using Twilio's
WhatsApp Sandbox — a free testing number Twilio provides so
individual developers can send WhatsApp messages without needing
a verified business account.

One-time setup required before this works — see README.md.

IMPORTANT LIMITATION: WhatsApp only allows free-form messages within
24 hours of your last message TO the sandbox number. If that window
has closed, sending fails with a "ContentSid Required" error. The
fix is simple: send any message to the sandbox number from your
phone, which reopens the window for another 24 hours.
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    MY_WHATSAPP_NUMBER,
)


def send_whatsapp_message(message: str) -> str:
    """
    Sends `message` to MY_WHATSAPP_NUMBER via Twilio's WhatsApp Sandbox.
    Returns the message SID on success.

    Raises a clear, friendly error (instead of a raw Twilio traceback)
    if the 24-hour session window has closed.
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        sent = client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
            to=f"whatsapp:{MY_WHATSAPP_NUMBER}",
            body=message,
        )
        return sent.sid

    except TwilioRestException as e:
        if "ContentSid" in str(e):
            raise RuntimeError(
                "WhatsApp session window closed (this resets every 24h).\n"
                "Fix: open WhatsApp on your phone and send any message "
                "to the Twilio sandbox number, then run this script again."
            ) from e
        raise  # re-raise anything else as-is, we don't want to hide real bugs


if __name__ == "__main__":
    sid = send_whatsapp_message("Test message from Daily Briefing Bot!")
    print(f"Sent. Message SID: {sid}")
