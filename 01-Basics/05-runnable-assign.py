from langchain_core.runnables import (
    RunnableAssign,
    RunnableParallel,
    RunnableLambda
)

"""
===========================================================
RunnableAssign - LangChain Runnable Component
===========================================================

What is RunnableAssign?
----------------------
RunnableAssign is a LangChain Runnable component used to add
new information (new keys/values) to an existing dictionary
without removing the original data.

It extends the existing input with additional calculated
results.

Why do we need RunnableAssign?
------------------------------
In AI applications, we often need to enrich existing data.

Example:
Before RunnableAssign:

{
    "question": "What is LangChain?"
}

After RunnableAssign:

{
    "question": "What is LangChain?",
    "word_count": 3,
    "category": "AI"
}

The original information is preserved and new information
is added.

How does RunnableAssign work?
-----------------------------

Input Dictionary
        |
        v
RunnableAssign
        |
        +----------------+
        |                |
        v                v
 Existing Data     New Processing
                     |
                     v
              New Fields Added
        |
        v

Final Dictionary


RunnableAssign internally uses RunnableParallel
to calculate the new fields.

Example:

RunnableAssign(
    RunnableParallel(
        word_count=word_counter
    )
)


Real-world AI Applications:
---------------------------

1. RAG (Retrieval Augmented Generation)

User Question:

{
    "question": "What is refund policy?"
}

After retrieval:

{
    "question": "What is refund policy?",
    "context": "Refund allowed within 30 days"
}


2. AI Agents

Existing state:

{
    "user_query": "...",
}

Add:

{
    "intent": "claim",
    "confidence": 0.95
}


3. Document Processing

Original:

{
    "document": pdf_text
}

Add:

{
    "summary": "...",
    "keywords": [...]
}


Important Difference:
---------------------

RunnableParallel:
- Creates a new dictionary with outputs.
- Does not preserve input automatically.

RunnableAssign:
- Keeps existing dictionary.
- Adds new fields.

Example:

RunnableParallel output:

{
    "word_count": 6
}


RunnableAssign output:

{
    "text": "...",
    "word_count": 6
}


Important Rule:
---------------

RunnableLambda receives whatever previous component sends.

If previous component sends a dictionary:

{
    "text": "hello"
}

then function should handle dictionary:

def count_words(data):
    text = data["text"]
    return len(text.split())


===========================================================
"""

def word_count(data):
    text = data["text"]
    return len(text.split())


word_counter = RunnableLambda(word_count)


assign = RunnableAssign(
    RunnableParallel(
        word_count=word_counter
    )
)


data = {
    "text": "LangChain helps us build AI applications"
}


result = assign.invoke(data)

print(result)