"""
agent.py
--------
This is what upgrades the project from a fixed "pipeline" into an
actual agent. Instead of main.py always calling get_weather(),
get_top_news(), and get_todos() in the same hardcoded order, we hand
Gemini the *functions themselves* as tools and let the model decide
which ones it actually needs to answer the request.

This is called "automatic function calling": you pass real Python
functions as tools, and the SDK handles calling them and feeding
the results back to the model for you.
"""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from weather import get_weather
from news import get_top_news
from todo import get_todos

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = """You are my personal morning briefing assistant.
You have tools to check the weather, get news headlines, and read my
to-do list. Call only the tools you actually need to answer my request
— don't call a tool just because it exists.
Write your final answer as a short, warm briefing under 150 words,
plain text, no markdown headers or bullet symbols. Write it like a
person speaking to me, not a report."""


def run_agent(user_request: str) -> str:
    """
    user_request: what you're asking for, in plain English, e.g.
        "Give me my full morning briefing"
        "Just the weather and my tasks, skip the news today"
        "Any news about AI? I don't need weather or tasks"

    The SDK automatically calls whichever of get_weather / get_top_news /
    get_todos the model decides it needs, then returns the model's
    final written answer.
    """
    # Using Chat here (not a one-off generate_content call) is the
    # SDK's recommended way to use automatic function calling — it
    # keeps the tool-call results in context properly.
    chat = client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[get_weather, get_top_news, get_todos],
        ),
    )

    response = chat.send_message(user_request)
    return response.text


if __name__ == "__main__":
    # Try changing this request and see which tools the agent
    # decides to call — that's the whole point of the upgrade.
    print(run_agent("Give me my full daily briefing."))
