from langchain_core.runnables import RunnableBranch, RunnableLambda


def is_policy_question(text):
    return "policy" in text.lower()


def is_claim_question(text):
    return "claim" in text.lower()


def policy_response(text):
    return "It is a policy related question"


def claim_response(text):
    return "It is a claim related question"


def general_response(text):
    return "General conversation"


policy_runnable = RunnableLambda(policy_response)

claim_runnable = RunnableLambda(claim_response)

general_runnable = RunnableLambda(general_response)


branch = RunnableBranch(
    (is_policy_question, policy_runnable),
    (is_claim_question, claim_runnable),
    general_runnable
)


result = branch.invoke(
    "What is the policy for claim?"
)

print(result)