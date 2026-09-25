"""
news.py
-------
Talks to the Currents API and returns today's top headlines
for a given topic. Chosen over NewsAPI.org because it only
needs a normal email to sign up — no work/company email required.
"""

import requests
from config import NEWS_API_KEY, NEWS_TOPIC


def get_top_news(count=5):
    """
    Fetch top headlines related to NEWS_TOPIC.

    Returns a list of dicts like:
    [{"title": "...", "source": "...", "url": "..."}, ...]
    """
    url = "https://api.currentsapi.services/v1/search"

    params = {
        "keywords": NEWS_TOPIC,
        "apiKey": NEWS_API_KEY,
        "language": "en",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    headlines = []
    # Currents returns articles under the "news" key, not "articles"
    for article in data.get("news", [])[:count]:
        headlines.append({
            "title": article["title"],
            "source": article.get("author") or "Currents",
            "url": article["url"],
        })

    return headlines


if __name__ == "__main__":
    for item in get_top_news():
        print(f"- {item['title']} ({item['source']})")
