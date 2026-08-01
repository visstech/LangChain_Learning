"""
===========================================================
RunnableAssign - LangChain Runnable Component
===========================================================

What is RunnableAssign?
-----------------------

RunnableAssign is used to add new information to an
existing dictionary without removing the existing data.


Before RunnableAssign:

{
    "question": "What is LangChain?"
}


After RunnableAssign:

{
    "question": "What is LangChain?",
    "word_count": 3
}


Why do we need RunnableAssign?
------------------------------

AI applications continuously enrich data.

Example:

User Question:

{
    "question": "What is RAG?"
}


After processing:

{
    "question": "What is RAG?",
    "category": "AI",
    "length": 3,
    "sentiment": "neutral"
}


Real-world Applications:
------------------------

1. RAG Applications

Original:

{
    "question": "Explain refund policy"
}


Add:

{
    "context": "Refund allowed within 30 days"
}


2. Document Processing

PDF Text

Add:

{
    "summary": "...",
    "keywords": [...]
}


3. AI Agents

Agent State:

{
    "user_request": "Book flight"
}


Add:

{
    "intent": "travel",
    "confidence": 0.95
}


Important Difference:

RunnableParallel:

Creates new output dictionary.

Example:

{
 "word_count": 5
}


RunnableAssign:

Keeps old data and adds new fields.

Example:

{
 "text": "...",
 "word_count": 5
}


===========================================================
"""


from langchain_core.runnables import (
    RunnableAssign,
    RunnableParallel,
    RunnableLambda
)


# Function receives dictionary

def word_count(data):

    text = data["text"]

    return len(text.split())


def character_count(data):

    text = data["text"]

    return len(text)


word_counter = RunnableLambda(word_count)

character_counter = RunnableLambda(character_count)


# Create Assign Pipeline

assign = RunnableAssign(

    RunnableParallel(

        word_count=word_counter,

        character_count=character_counter

    )

)


input_data = {

    "text": "LangChain helps us build AI applications"

}


result = assign.invoke(input_data)


print(result)