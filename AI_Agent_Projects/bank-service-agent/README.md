# Bank Customer Service Agent

A simulated bank customer service chatbot built with Gemini's
function-calling (agentic tool use) and a Streamlit chat interface.

**This is a portfolio/learning project.** It uses a fake local
database and never connects to any real bank. Building it this way
is intentional — it lets you focus on the AI agent design and
security patterns that real banking agents actually use, without
needing real financial data or credentials.

## Architecture

```
Login (auth.py, plain code)
        │
        ▼
Streamlit chat (app.py)
        │
        ▼
Gemini agent (agent.py) ──► decides which tool(s) it needs
        │
        ├──► get_balance()
        ├──► get_recent_transactions()
        ├──► block_card()          (requires confirmation first)
        └──► file_dispute()        (requires confirmation first)
                │
                ▼
        SQLite database (bank.db) — scoped to the logged-in customer only
```

## Key design decisions (worth understanding, not just running)

- **Login is NOT handled by the AI.** Identity verification
  (`auth.py`) is plain, predictable code — never delegate "who is
  this person" to an LLM.
- **Every tool is scoped to the logged-in customer automatically.**
  The agent is never given a customer ID to fill in itself — it
  can't look up anyone else's data even if a message tried to trick
  it into doing so, because the tools themselves only ever read
  `tools.CURRENT_CUSTOMER_ID`, which the app sets at login.
- **State-changing actions require confirmation.** The system prompt
  instructs the agent to explain what it's about to do and get a
  "yes" before calling `block_card` or `file_dispute` — mirroring how
  real banking agents avoid irreversible mistakes from a single
  ambiguous message.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Get a free Gemini API key

https://aistudio.google.com/app/apikey

## 3. Set up your .env file

```bash
cp .env.example .env
```

Paste your Gemini key in.

## 4. Create the sample database

```bash
python database.py
```

This creates `bank.db` with two fake customers you can log in as.

## 5. Run the app

```bash
streamlit run app.py
```

Your browser will open automatically. Log in with:
- Customer ID: `cust001`, PIN: `1234` (Priya Sharma)
- Customer ID: `cust002`, PIN: `5678` (Ahmad Faizal)

## Things to try in the chat

- "What's my balance?"
- "Show me my recent transactions"
- "I don't recognize a charge, I want to dispute it" → the agent
  should ask which transaction and why *before* filing anything
- "My card was stolen, block it" → same — it should confirm first
- Try asking something outside its scope, like "should I invest in
  stocks?" — it should decline and redirect rather than answer

## Example conversation:
    What's my balance?

  You currently have two accounts:

  Checking: $2,450.75
  Savings: $8,900.00
  Is there anything else I can help you with today?

  I see a charge I don't recognize on my account, I want to dispute it

  I can certainly help you file a dispute for any unrecognized charges.

  Here are your recent debit transactions:

  Aug 20: $85.40 at Grocery Store
  Aug 18: $120.00 for Electric Bill
  Aug 17: $6.50 at Coffee Shop
  Aug 15: $450.00 at Unknown Merchant XZ99
  Are you referring to the $450.00 charge from Unknown Merchant XZ99 on Aug 15?

  If so, please confirm if you would like me to go ahead and file a dispute for this transaction.

  Yes, go ahead

  I have filed the dispute for the $450.00 charge from Unknown Merchant XZ99 (Transaction ID: t005).

  A case manager will review your claim within 5 business days, and we will follow up with you on the progress.

  Since this charge was unrecognized, would you also like me to block your card to prevent any further unauthorized activity?

  Yes. Please block my cared immediately

  Your card has been successfully blocked, so no new charges can be processed on it.

  To order a replacement card or if you need any additional assistance, please let me know or reach out to our support team. Is there anything else I can help you with today?


## Next steps to go further

- **Add more tools**: transfer between the customer's own accounts,
  set up a recurring payment, update contact info
- **Add logging**: record every tool call to a file, so you have an
  audit trail — real banks require this
- **Add rate limiting / lockout**: block login after 3 failed PIN
  attempts
- **Swap SQLite for a mock REST API**: better mirrors how a real bank's
  backend would be structured, and is a good exercise in API design
- **Deploy it**: Streamlit Community Cloud hosts this kind of app free

## Project structure

```
bank-service-agent/
├── config.py       # loads Gemini API key
├── database.py      # creates and seeds the fake bank database
├── auth.py           # login verification (non-AI)
├── tools.py           # banking functions the agent can call
├── agent.py            # Gemini agent + system instruction (guardrails)
├── app.py                # Streamlit chat interface
├── .env.example            # template for your API key
└── requirements.txt        # Python dependencies
```
