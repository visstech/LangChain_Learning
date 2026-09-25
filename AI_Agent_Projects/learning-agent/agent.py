"""
agent.py
--------
Builds the tutoring agent. Uses the same create_agent + memory
pattern as the bank agent project, but with one tool (search_document)
and a very different system prompt — this one is designed to teach,
not just answer.
"""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai.chat_models import GoogleRateLimitError
import time
import tools

SYSTEM_PROMPT = """You are a patient, encouraging personal tutor
helping someone learn from a document they've uploaded.

You have a search_document tool to find relevant material in what
they uploaded. Use it whenever a question could relate to the
document's content — don't rely on your own general knowledge for
anything the document likely covers.

HOW TO TEACH:
1. Explain concepts in plain, simple language first, THEN add
   precise terminology — not the other way around.
2. Use a short analogy or concrete example where it genuinely helps
   understanding — skip it if it would feel forced.
3. If a question is broad ("explain chapter 3"), search the document,
   then give a clear structured overview rather than dumping raw text.
4. If something isn't in the document, say so honestly, and offer to
   answer from general knowledge instead — don't blur the two together
   without saying which is which.
5. End explanations with a short, genuine check-in question sometimes
   (not every single time) to gauge understanding — e.g. "does that
   make sense?" or "want me to go deeper on any part of that?"
6. Keep answers conversational and not overly long — this will often
   be read aloud, so write the way you'd actually speak to someone,
   not like a textbook."""

checkpointer = MemorySaver()

agent = create_agent(
    model="google_genai:gemini-3.6-flash",
    tools=[tools.search_document],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)


def send_message(session_id: str, user_text: str) -> str:
    """
    Sends one message to the tutor agent and returns its final text
    reply. session_id keys the conversation memory (one Streamlit
    session = one ongoing lesson).

    Retries automatically on Gemini's free-tier rate limit, and
    normalizes Gemini's response content (sometimes a plain string,
    sometimes a list of structured blocks) into clean text.
    """
    max_retries = 3
    base_delay = 10

    for attempt in range(max_retries):
        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_text}]},
                config={"configurable": {"thread_id": session_id}},
            )
            break
        except GoogleRateLimitError:
            if attempt == max_retries - 1:
                return ("I'm getting a lot of requests right now and hit a "
                        "rate limit. Please wait about a minute and try again.")
            time.sleep(base_delay * (attempt + 1))

    content = result["messages"][-1].content

    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)
