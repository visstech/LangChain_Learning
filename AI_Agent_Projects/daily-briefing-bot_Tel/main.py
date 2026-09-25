"""
main.py
-------
The entry point. This is what you run every morning.

Uses the agent (agent.py) to decide which tools it needs, then sends
the finished briefing to Telegram.
"""

from agent import run_agent
from telegram_bot import send_telegram_message


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

    print("\nSending to Telegram...")
    send_telegram_message(briefing_text)
    print("Sent! Check your Telegram.")


if __name__ == "__main__":
    main()
