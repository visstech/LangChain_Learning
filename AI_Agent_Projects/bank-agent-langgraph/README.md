# Bank Customer Service Agent — LangChain + PostgreSQL Edition

An upgraded version of the original bank agent project, rebuilt on:
- **PostgreSQL** instead of SQLite (a real production-grade database)
- **LangChain's `create_agent`** instead of calling the Gemini SDK directly
  (the current standard way to build tool-using agents, built on LangGraph)
- **4 new tools**, for 8 total
- **Real multi-turn memory** via LangGraph's checkpointer, so the agent
  remembers earlier parts of the conversation properly

Still a simulated bank on your own machine — never connects to a real bank.

## What changed from the original version, and why

| | Original (SQLite + raw Gemini SDK) | This version |
|---|---|---|
| Database | SQLite file | PostgreSQL (via Docker) |
| Agent framework | `google-genai` SDK directly | LangChain `create_agent` |
| Tool definition | Plain functions, type hints | `@tool`-decorated functions |
| Memory | None (single message in, single out) | Persistent per-session via checkpointer |
| Tool count | 4 | 8 |

**Why LangChain/LangGraph instead of calling Gemini directly?** The raw
SDK approach works fine for one model and simple cases. LangChain adds:
a standard interface that works across any LLM provider (swap Gemini for
Claude or GPT with one line), built-in conversation memory, and it's the
more common framework in real job postings — worth having on your resume
alongside the "built it from raw API calls" version.

## Architecture

```
Login (auth.py)
        │
        ▼
Streamlit chat (app.py)
        │
        ▼
LangChain agent (agent.py) ──► create_agent() decides which tool(s) to call
        │         (memory: MemorySaver checkpointer, keyed by customer_id)
        │
        ├──► get_balance()
        ├──► get_recent_transactions()
        ├──► get_dispute_status()          [NEW]
        ├──► block_card()                  (confirm first)
        ├──► file_dispute()                (confirm first)
        ├──► transfer_between_own_accounts()  [NEW] (confirm first)
        ├──► update_phone_number()         [NEW] (confirm first)
        └──► list_upcoming_bills()         [NEW]
                │
                ▼
        PostgreSQL — scoped to the logged-in customer only
```

## 1. Start PostgreSQL

You need Docker installed (https://www.docker.com/products/docker-desktop).

```bash
docker compose up -d
```

This starts a Postgres container with the database `bankdb`. Leave it
running in the background — `docker compose down` stops it when you're done.

## 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 3. Get a free Gemini API key

https://aistudio.google.com/app/apikey

## 4. Set up your .env file

```bash
cp .env.example .env
```

Paste in your Gemini key. Leave `DATABASE_URL` commented out unless you
changed the credentials in `docker-compose.yml`.

## 5. Create and seed the database

```bash
python database.py
```

## 6. Run the app

```bash
streamlit run app.py
```

Log in with `cust001` / `1234` (Priya) or `cust002` / `5678` (Ahmad).

## Things to try

- Everything from the original version (balance, transactions, dispute
  with confirmation, card block with confirmation)
- "Transfer $200 from my checking to my savings" — should confirm first
- "What's the status of my dispute on transaction t005?"
- "What bills do I have coming up?"
- "Update my phone number to +60111222333" — should confirm first
- Test memory: ask "what's my balance?", then later just ask "and my
  savings?" without repeating context — the agent should remember what
  you were just talking about

## Next steps to go further

- **Swap models with one line**: change `"google_genai:gemini-3.6-flash"`
  to `"anthropic:claude-sonnet-4-6"` in `agent.py` (with an Anthropic key)
  to see how provider-agnostic LangChain's interface really is
- **Persist memory to Postgres instead of in-process**: LangGraph supports
  a Postgres-backed checkpointer, so conversation history survives an
  app restart
- **Add LangSmith tracing**: see every tool call and reasoning step in a
  visual trace — genuinely useful for debugging agent behavior
- **Deploy Postgres to a free cloud tier** (Supabase, Neon) so the app
  isn't tied to your laptop

## Project structure

```
bank-agent-langgraph/
├── docker-compose.yml   # runs PostgreSQL locally
├── config.py             # loads API key and database URL
├── database.py            # creates and seeds the Postgres schema
├── auth.py                 # login verification (non-AI)
├── tools.py                  # 8 banking tools, @tool-decorated
├── agent.py                   # LangChain create_agent + memory
├── app.py                       # Streamlit chat interface
├── .env.example                  # template for your API key
└── requirements.txt               # Python dependencies
```
