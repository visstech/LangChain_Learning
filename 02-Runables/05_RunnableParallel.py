"""
===========================================================
RunnableParallel - LangChain Runnable Component
===========================================================

What is RunnableParallel?
-------------------------

RunnableParallel allows multiple independent tasks to run
using the same input at the same time.

Each Runnable receives the same input and produces its own
output.

Example:

                 Input
                   |
       +-----------+-----------+
       |           |           |
       v           v           v

    Task A      Task B      Task C

       |           |           |

       +-----------+-----------+

                   |
                   v

          Combined Dictionary


Why do we need RunnableParallel?
---------------------------------

In AI applications, we often need multiple analyses of the
same input.

Example:

Customer Review:

"The product is excellent"


Parallel Tasks:

1. Sentiment Analysis
2. Word Count
3. Language Detection


Output:

{
 "sentiment": "positive",
 "word_count": 4,
 "language": "English"
}


Real-world Applications:
------------------------

1. Document Analysis

PDF
 |
 +--> Summary
 |
 +--> Keywords
 |
 +--> Classification


2. Customer Support AI

Message
 |
 +--> Sentiment
 |
 +--> Intent
 |
 +--> Priority


3. RAG Systems

Question
 |
 +--> Retrieve Documents
 |
 +--> Detect Intent
 |
 +--> Extract Metadata


Important Difference:

RunnableSequence:

A --> B --> C

(one after another)


RunnableParallel:

       A
      /
Input
      \
       B

(multiple at the same time)


===========================================================
"""


from langchain_core.runnables import (
    RunnableParallel,
    RunnableLambda,
    RunnablePassthrough
)


def word_count(text):
    return len(text.split())


def character_count(text):
    return len(text)


def make_upper(text):
    return text.upper()


word_counter = RunnableLambda(word_count)

character_counter = RunnableLambda(character_count)

upper_converter = RunnableLambda(make_upper)


chain = RunnableParallel(

    original_text=RunnablePassthrough(),

    word_count=word_counter,

    character_count=character_counter,

    uppercase=upper_converter
)


result = chain.invoke(
    "LangChain helps us build AI applications"
)


print(result)