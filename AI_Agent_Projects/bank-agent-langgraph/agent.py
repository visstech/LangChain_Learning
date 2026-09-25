"""
agent.py
--------
Builds the agent using LangChain's create_agent — the current
recommended API (stable since LangGraph v1.0, Oct 2025), which
replaces the older langgraph.prebuilt.create_react_agent.

create_agent handles the whole reasoning loop for you: send a
message, it decides which tool(s) to call, runs them, and keeps
going until it has a final answer.

We attach a MemorySaver checkpointer so the conversation has real
memory across turns — each customer's session is identified by a
thread_id (we use their customer_id).
"""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai.chat_models import GoogleRateLimitError
import time
import tools

SYSTEM_PROMPT = """You are a customer service assistant for a bank.
The customer you're speaking to is already logged in and verified —
you never need to ask for their identity, account number, or PIN.

You have tools to check balances, look up transactions, check a
dispute's status, block a card, file a dispute, transfer money
between the customer's own accounts, update their phone number, and
list upcoming bills.

STRICT RULES YOU MUST FOLLOW:
1. Before calling block_card, file_dispute, transfer_between_own_accounts,
   or update_phone_number — all of these change real account state —
   you MUST first explain what you're about to do and get explicit
   confirmation from the customer (e.g. they say "yes" or "go ahead").
   Never call these on the first message that mentions a request.
2. Only discuss this customer's own accounts. You cannot see or
   affect anyone else's data.
3. If a request is outside normal banking support (legal advice,
   investment recommendations, anything unrelated to their account),
   say so plainly and suggest the right department instead of
   attempting it yourself.
4. If a customer seems distressed about potential fraud, stay calm
   and reassuring, gather details, and explain what happens next.
5. Keep responses concise and conversational, like a helpful human
   support agent — not a legal document."""

checkpointer = MemorySaver()

agent = create_agent(
    model="google_genai:gemini-3.6-flash",
    tools=tools.ALL_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)


def send_message(customer_id: str, user_text: str) -> str:
    """
    Sends one user message to the agent and returns its final text
    reply. customer_id doubles as the memory "thread" so each
    customer's conversation history stays separate.

    Gemini sometimes returns message content as a plain string, and
    sometimes as a list of structured blocks (e.g. text plus internal
    metadata like a signature). This handles both cases so the caller
    always gets back clean, displayable text.

    Also retries automatically (with increasing wait times) if
    Gemini's free-tier rate limit is hit, instead of crashing the app.
    """
    max_retries = 3
    base_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_text}]},
                config={"configurable": {"thread_id": customer_id}},
            )
            break  # success, exit the retry loop
        except GoogleRateLimitError:
            if attempt == max_retries - 1:
                # Out of retries — give a clear message instead of a crash.
                return ("I'm getting a lot of requests right now and hit a "
                        "rate limit. Please wait about a minute and try again.")
            wait_time = base_delay * (attempt + 1)  # 10s, then 20s, then 30s
            time.sleep(wait_time)

    content = result["messages"][-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        return "".join(text_parts)

    return str(content)  # fallback, shouldn't normally happen