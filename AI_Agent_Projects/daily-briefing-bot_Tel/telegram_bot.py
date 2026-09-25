"""
telegram.py
-----------
Sends the finished briefing to Telegram instead of WhatsApp.

Why Telegram instead of Twilio/WhatsApp: Telegram's Bot API is
completely free with no trial limits, no paywalled features, and no
24-hour session window to manage — you send a message whenever you
want, forever. Much better fit for a script that runs automatically
every day. One-time setup required — see README.md.
"""

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message: str) -> dict:
    """
    Sends `message` to TELEGRAM_CHAT_ID via your Telegram bot.
    Returns Telegram's response as a dict.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    response = requests.post(url, data=payload, timeout=10)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = send_telegram_message("Test message from Daily Briefing Bot!")
    print(result)
