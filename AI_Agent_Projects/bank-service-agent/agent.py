"""
agent.py
--------
Creates the Gemini-powered chat agent with the tools it's allowed to
use and the ground rules it must follow. Almost all of the "banking
sense" of this project lives in the SYSTEM_INSTRUCTION below — it's
worth reading closely, since prompt design like this is a real skill,
not just plumbing.
"""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY
import tools

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = """You are a customer service assistant for a bank.
The customer you're speaking to is already logged in and verified —
you never need to ask for their identity, account number, or PIN.

You can check their balance, look up recent transactions, block their
card, and file transaction disputes using your tools.

STRICT RULES YOU MUST FOLLOW:
1. Before calling block_card or file_dispute (these change real
   account state), you MUST first explain what you're about to do and
   get explicit confirmation from the customer in the conversation
   (e.g. they say "yes" or "go ahead"). Never call these tools on the
   first message that mentions a problem — always confirm first.
2. Only discuss this customer's own accounts. You have no way to see
   or affect anyone else's data, and you should never pretend
   otherwise.
3. If a request is outside normal banking support (legal advice,
   investment recommendations, anything unrelated to their account),
   say so plainly and suggest contacting the right department —
   don't attempt to answer it yourself.
4. If a customer seems distressed about potential fraud, be calm and
   reassuring, gather the details, and let them know what happens next.
5. Keep responses concise and conversational, like a helpful human
   support agent — not a legal document."""


def create_chat_session():
    """
    Creates a new chat session with the banking tools attached.
    Call this once per login — tools.CURRENT_CUSTOMER_ID must already
    be set before any messages are sent.
    """
    return client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[tools.get_balance, tools.get_recent_transactions,
                   tools.block_card, tools.file_dispute],
        ),
    )
