# Daily Briefing Bot

A beginner-friendly AI **agent** that decides for itself which tools
it needs — weather, news, your to-do list — to answer your request,
then sends the result straight to your WhatsApp.

## How it works

```
                    ┌──► get_weather()
User request ──► Gemini decides ──► get_top_news()  ──► WhatsApp message
   (agent.py)       which tools     get_todos()
                    to call
```

Unlike a fixed pipeline that always calls the same three functions
in the same order, `agent.py` hands Gemini the *functions themselves*
as tools and lets the model decide which ones it actually needs. This
is real agentic behavior — ask it "just give me the news" and it will
skip weather and todos entirely.

## 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 2. Get your free API keys

- **OpenWeatherMap**: sign up at https://openweathermap.org/api (free tier)
- **Currents API**: sign up at https://currentsapi.services/en/register
  (just needs a normal email)
- **Google Gemini**: get a free key at https://aistudio.google.com/app/apikey
  (sign in with a Google account, no card required)

## 3. Set up Telegram (free, no paywall, no daily reset)

1. Open Telegram and search for **@BotFather** (the official bot for creating bots)
2. Send `/newbot` and follow the prompts — give it any name and username
3. BotFather replies with a **token** like `123456789:ABCdefGhIjKlmNoPQRstuVwxyz` — this is `TELEGRAM_BOT_TOKEN`
4. Search for your new bot by its username and send it any message (e.g. "hi") — bots can't message you first
5. In your browser, visit:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   (replace `<YOUR_TOKEN>` with your real token)
6. Look for `"chat":{"id":123456789,...}` in the response — that number is your `TELEGRAM_CHAT_ID`

That's it — no verification, no trial limits, no 24-hour session window to manage.

## 4. Set up your .env file

```bash
cp .env.example .env
```

Fill in all your API keys, plus:
- `TELEGRAM_BOT_TOKEN` — from BotFather
- `TELEGRAM_CHAT_ID` — from the getUpdates step above

## 5. Add your to-do list

Edit `todo.txt` — one task per line.

## 6. Run it

```bash
python main.py
```

You'll see the briefing printed in your terminal, and it'll also land
in Telegram within a few seconds.

## Note on WhatsApp (an earlier version used this)

An earlier version of this project sent briefings via Twilio's free
WhatsApp Sandbox. It worked, but had two real limitations discovered
along the way: WhatsApp requires messages to use a pre-approved
Content Template, and Twilio's Content Template Builder is paywalled
on trial accounts — so building a custom template wasn't possible
without adding funds. Telegram avoids both problems entirely, which
is why this version uses it. `whatsapp.py` is still in this folder
if you want to see that approach or revisit it later with a paid
Twilio account.

## Next steps (once this works)

- **Schedule it**: use `cron` (Mac/Linux) or Task Scheduler (Windows)
  to run `main.py` automatically every morning.
- **Try different requests**: change the string in `main.py`'s
  `run_agent(...)` call — e.g. `"Just the weather and my tasks, skip
  the news"` — and watch the agent call fewer tools.
- **Add error handling**: what should happen if the weather API is
  down? Right now the whole script would crash — a good next
  exercise is wrapping each fetch in a try/except.

## Project structure

```
daily-briefing-bot/
├── config.py       # loads API keys and settings
├── weather.py       # weather tool
├── news.py          # news tool (via Currents API)
├── todo.py           # to-do list tool
├── agent.py          # the agent: lets Gemini decide which tools to call
├── whatsapp.py       # (legacy) Twilio WhatsApp sender \u2014 hit paywall issues
├── telegram_bot.py   # sends the final briefing via Telegram
├── briefing.py       # (legacy) fixed pipeline version — kept for comparison
├── main.py           # entry point: runs the agent, sends to WhatsApp
├── todo.txt           # your task list (edit this)
├── .env.example       # template for your API keys
└── requirements.txt   # Python dependencies
```
