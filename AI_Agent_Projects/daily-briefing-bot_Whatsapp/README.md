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

## 3. Set up WhatsApp sending (Twilio Sandbox — free)

Twilio's Sandbox is a free way for individual developers to send
WhatsApp messages without a verified business account.

1. Sign up at https://www.twilio.com/try-twilio (free, no charge for sandbox use)
2. In the Twilio Console, go to **Messaging → Try it out → Send a WhatsApp message**
3. You'll see a sandbox number (usually `+1 415 523 8886`) and a join
   code like `join happy-tiger`
4. From your own WhatsApp, send that exact join message to that number
   — this opts your number into the sandbox (required once)
5. Back in the Twilio Console, find your **Account SID** and **Auth
   Token** on the main dashboard

## 4. Set up your .env file

```bash
cp .env.example .env
```

Fill in all your API keys, plus:
- `TWILIO_WHATSAPP_FROM` — the sandbox number, in `+1415...` format
- `MY_WHATSAPP_NUMBER` — your own number, with country code (e.g. `+60123456789`)

## 5. Add your to-do list

Edit `todo.txt` — one task per line.

## 6. Run it

```bash
python main.py
```

You'll see the briefing printed in your terminal, and it'll also land
in your WhatsApp within a few seconds.

## Note on the Twilio Sandbox

The sandbox is free but has two limits worth knowing:
- Your WhatsApp number needs to re-send the join code roughly every
  72 hours to stay connected (Twilio will remind you)
- Only numbers that have joined the sandbox can receive messages —
  fine for a personal project sending to yourself

If you ever want this running unattended for months without
re-joining, Twilio's paid WhatsApp Business API removes that limit
— not necessary for a resume project.

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
├── whatsapp.py       # sends the final briefing via Twilio WhatsApp
├── briefing.py       # (legacy) fixed pipeline version — kept for comparison
├── main.py           # entry point: runs the agent, sends to WhatsApp
├── todo.txt           # your task list (edit this)
├── .env.example       # template for your API keys
└── requirements.txt   # Python dependencies
```
