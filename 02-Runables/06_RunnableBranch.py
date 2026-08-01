"""
===========================================================
RunnableBranch - LangChain Runnable Component
===========================================================

What is RunnableBranch?
-----------------------

RunnableBranch is used to create conditional workflows
in LangChain.

It works similar to Python if-elif-else statements.

Based on a condition, it selects which Runnable should
execute.


Python Example:

if condition:
    execute A
else:
    execute B


LangChain Example:

              Input
                |
                v
            Condition
             /     \
          True     False
           |         |
           v         v
      Runnable A  Runnable B


Why do we need RunnableBranch?
------------------------------

Real AI applications need decision-making.

Example: Customer Support AI


User Message

      |
      v

Intent Detection

      |
 +----+----------------+
 |                     |
 v                     v

Policy Question     Claim Question

 |                     |

Policy Agent       Claim Agent


Real-world Applications:
------------------------

1. Insurance AI Assistant

Question
   |
   +--> Policy Related
   |
   +--> Claim Related
   |
   +--> General Query


2. Customer Support

Message
   |
   +--> Complaint
   |
   +--> Feedback
   |
   +--> Information Request


3. AI Agent Routing

User Request
   |
   +--> Search Tool
   |
   +--> Calculator Tool
   |
   +--> Database Tool


Important:

Condition function should return:

True / False


Response function should return:

Actual output


===========================================================
"""


from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda
)


# ----------------------------
# Condition Functions
# ----------------------------

def is_policy_question(text):
    return "policy" in text.lower()


def is_claim_question(text):
    return "claim" in text.lower()


# ----------------------------
# Response Functions
# ----------------------------

def policy_response(text):
    return "This is a policy related question."


def claim_response(text):
    return "This is a claim related question."


def general_response(text):
    return "This is a general question."


# Convert functions into Runnables

policy_runnable = RunnableLambda(policy_response)

claim_runnable = RunnableLambda(claim_response)

general_runnable = RunnableLambda(general_response)


# Create Branch

branch = RunnableBranch(

    (is_policy_question, policy_runnable),

    (is_claim_question, claim_runnable),

    general_runnable
)


# Test

result = branch.invoke(
    "How can I check my policy details?"
)


print(result)