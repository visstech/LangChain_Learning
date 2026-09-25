"""
weather.py
----------
Talks to the OpenWeatherMap API and returns today's weather
as a simple Python dictionary.
"""

import requests
from config import OPENWEATHER_API_KEY, CITY


def get_weather() -> dict:
    """
    Fetch current weather for CITY.

    Returns a dict like:
    {
        "city": "Kuala Lumpur",
        "temp": 31.2,
        "feels_like": 35.0,
        "description": "scattered clouds",
        "humidity": 70
    }
    """
    url = "https://api.openweathermap.org/data/2.5/weather"

    # 'params' becomes the query string, e.g. ?q=Kuala Lumpur&appid=...
    params = {
        "q": CITY,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",  # so we get Celsius instead of Kelvin
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # raises an error if the API call failed
    data = response.json()

    return {
        "city": data["name"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
    }


# This block only runs if you execute "python weather.py" directly —
# handy for testing this one piece in isolation.
if __name__ == "__main__":
    print(get_weather())
