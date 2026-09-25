"""
main.py
-------
The entry point. This is what you run every morning.
It calls each module in order and prints the final briefing.
"""

from weather import get_weather
from news import get_top_news
from todo import get_todos
from briefing import generate_briefing


def main():
    print("Fetching your daily briefing...\n")

    weather = get_weather()
    news = get_top_news()
    todos = get_todos()

    briefing_text = generate_briefing(weather, news, todos)

    print("=" * 50)
    print("YOUR DAILY BRIEFING")
    print("=" * 50)
    print(briefing_text)
    print("=" * 50)


if __name__ == "__main__":
    main()
