"""
config.py
---------
Loads settings and API keys from a .env file so we never hard-code
secrets directly into our source code (this matters even for small
projects — it's a real habit worth building early).
"""

import os
from dotenv import load_dotenv

# Reads the .env file in this folder and loads its values into
# the environment, so os.getenv() below can find them.
load_dotenv()

# --- API Keys (get these for free, see README.md) ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Twilio (WhatsApp sending) ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # Twilio's sandbox number
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")      # your number, e.g. +60123456789

# --- Personal settings (edit these in .env, not here) ---
CITY = os.getenv("CITY", "Kuala Lumpur")
NEWS_TOPIC = os.getenv("NEWS_TOPIC", "technology")
