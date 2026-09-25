"""
config.py
---------
Loads settings from a .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Matches the docker-compose.yml credentials by default.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bankuser:bankpass@localhost:5432/bankdb",
)
