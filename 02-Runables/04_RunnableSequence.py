"""
===========================================================
RunnableSequence - LangChain Runnable Component
===========================================================

What is RunnableSequence?
-------------------------
RunnableSequence is used to execute multiple LangChain
components one after another in a fixed order.

The output of one component becomes the input of the next
component.

It is created using the pipe (|) operator.

Example:

Step 1  -->  Step 2  -->  Step 3

Input
 |
 v
Prompt
 |
 v
LLM
 |
 v
Output Parser
 |
 v
Final Output


Why do we need RunnableSequence?
---------------------------------

Many AI applications require multiple steps:

Example: AI Question Answering

User Question
      |
      v
Create Prompt
      |
      v
Send to LLM
      |
      v
Format Response


Real-world Applications:
------------------------

1. Chatbots

User Input
   |
Prompt Template
   |
LLM
   |
Response


2. Document Summarization

Document
   |
Prompt
   |
LLM
   |
Summary


3. RAG Pipeline

Question
   |
Retriever
   |
Prompt
   |
LLM
   |
Answer


===========================================================
"""


from langchain_core.runnables import (
    RunnableLambda,
    RunnableSequence
)


# Step 1
def add_prefix(text):
    return f"Question: {text}"


# Step 2
def convert_upper(text):
    return text.upper()


prefix_runnable = RunnableLambda(add_prefix)

upper_runnable = RunnableLambda(convert_upper)


# Creating sequence

chain = RunnableSequence(
    prefix_runnable,
    upper_runnable
)


result = chain.invoke(
    "What is LangChain?"
)


print(result)