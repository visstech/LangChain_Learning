# Daily Briefing Bot

A beginner-friendly AI agent that fetches your weather, top news, and
to-do list every morning, then uses Google Gemini (free tier) to turn
it into one short, readable briefing.

## How it works

```
Weather API ─┐
News API ────┼──► Gemini (writes a natural summary) ──► Printed to console
To-Do file ──┘
```

Each data source is its own small module (`weather.py`, `news.py`,
`todo.py`). `main.py` calls them, then hands everything to
`briefing.py`, which asks Gemini to write a short human-sounding
summary instead of you reading three raw blocks of data.

**Why Gemini instead of Claude here?** Google's Gemini API has a
genuinely ongoing free tier with rate limits — no credit card, no
trial credit that runs out. That makes it a better fit while you're
learning and running this daily. (The Anthropic API works great too,
but it's pay-as-you-go after a small one-time trial credit — worth
switching back to once you're past the learning stage.)

## 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

(If you're using a virtual environment, activate it first:
`python -m venv venv` then `source venv/bin/activate` on
Mac/Linux, or `venv\Scripts\activate` on Windows.)

## 2. Get your free API keys

- **OpenWeatherMap**: sign up at https://openweathermap.org/api (free tier)
- **Currents API**: sign up at https://currentsapi.services/en/register
  (just needs a normal email — no work/company email required)
- **Google Gemini**: get a free key at https://aistudio.google.com/app/apikey
  (sign in with a Google account, no card required)

## 3. Set up your .env file

Copy the example file and fill in your real keys:

```bash
cp .env.example .env
```

Then open `.env` and paste in your actual API keys, plus your city
and preferred news topic.

## 4. Add your to-do list

Edit `todo.txt` — one task per line.

## 5. Run it

```bash
python main.py
```

You should see a short, friendly morning briefing printed to your
terminal.

## Next steps (once this works)

- **Schedule it**: use `cron` (Mac/Linux) or Task Scheduler (Windows)
  to run `main.py` automatically every morning.
- **Deliver it somewhere better than the console**: send it to
  yourself via a Telegram bot or email instead of just printing it.
- **Make it more "agentic"**: right now the pipeline is fixed
  (always fetch weather → news → todos → summarize). A more advanced
  version could let Claude *decide* which sources to check using
  tool use / function calling — e.g., only pulling news if you ask
  for it, or fetching calendar events too.
- **Add error handling**: what should happen if the weather API is
  down? Right now the whole script would crash — a good next
  exercise is wrapping each fetch in a try/except.

## Project structure

```
daily-briefing-bot/
├── config.py       # loads API keys and settings
├── weather.py       # fetches weather data
├── news.py          # fetches news headlines (via Currents API)
├── todo.py           # reads your to-do list
├── briefing.py      # asks Gemini to summarize everything
├── main.py           # runs the whole pipeline
├── todo.txt          # your task list (edit this)
├── .env.example      # template for your API keys
└── requirements.txt  # Python dependencies
```
