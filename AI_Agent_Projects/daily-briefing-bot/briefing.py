"""
briefing.py
-----------
This is the "AI" part of the AI agent. It takes the raw weather,
news, and to-do data and asks Google Gemini (free tier, no card
required) to turn it into a short, natural-sounding morning
briefing — instead of you reading three separate blocks of raw data.

Uses the current google-genai SDK (the old google-generativeai
package was retired by Google and no longer works).
"""

from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

# gemini-2.5-flash is fast, capable, and covered by the free tier.
# Check https://ai.google.dev/gemini-api/docs/models for the latest
# model names if this one is ever retired.
MODEL_NAME = "gemini-3.6-flash"


def generate_briefing(weather, news, todos):
    """
    weather: dict from weather.get_weather()
    news:    list from news.get_top_news()
    todos:   list from todo.get_todos()

    Returns a short briefing as a string.
    """
    # Turn the news list into readable lines like "- Title (Source)"
    news_text = "\n".join(f"- {n['title']} ({n['source']})" for n in news)

    # Same for the to-do list, with a fallback if it's empty
    todo_text = "\n".join(f"- {t}" for t in todos) if todos else "No tasks added for today."

    prompt = f"""You are my personal morning briefing assistant.
Turn the raw data below into a short, warm, well-organized morning
briefing under 150 words. Plain text, no markdown headers or bullet
symbols — write it like a person speaking to me, not a report.

WEATHER
City: {weather['city']}
Temperature: {weather['temp']}°C (feels like {weather['feels_like']}°C)
Conditions: {weather['description']}
Humidity: {weather['humidity']}%

TOP NEWS
{news_text}

TODAY'S TASKS
{todo_text}

Write the briefing now."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text


if __name__ == "__main__":
    # Quick manual test with fake data, so you don't burn API
    # calls to weather/news just to test this file.
    fake_weather = {"city": "Kuala Lumpur", "temp": 31, "feels_like": 35,
                     "description": "scattered clouds", "humidity": 70}
    fake_news = [{"title": "AI breakthrough announced", "source": "TechCrunch"}]
    fake_todos = ["Finish resume", "Submit assignment"]

    print(generate_briefing(fake_weather, fake_news, fake_todos))
