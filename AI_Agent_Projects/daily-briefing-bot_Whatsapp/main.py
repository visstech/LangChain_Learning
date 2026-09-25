"""
main.py
-------
The entry point. This is what you run every morning.

This version uses the agent (agent.py) instead of calling weather,
news, and todos directly in a fixed order — the model itself decides
what it needs based on the request you give it. Once generated, the
briefing is sent straight to your WhatsApp.
"""

from agent import run_agent
from whatsapp import send_whatsapp_message


def main():
    print("Fetching your daily briefing...\n")

    briefing_text = run_agent(
        "Give me my full daily briefing including weather, news, and my tasks."
    )

    print("=" * 50)
    print("YOUR DAILY BRIEFING")
    print("=" * 50)
    print(briefing_text)
    print("=" * 50)

    print("\nSending to WhatsApp...")
    send_whatsapp_message(briefing_text)
    print("Sent! Check your WhatsApp.")


if __name__ == "__main__":
    main()
