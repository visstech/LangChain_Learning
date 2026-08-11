"""
=====================================================

Topic:
Building a Memory-Enabled AI Agent

Concepts Covered:

- Conversation Memory
- HumanMessage
- AIMessage
- ToolMessage
- Message History
- Stateful AI Agent
- Custom Business Tools
- ChatOllama
- Qwen2.5

Architecture:


                    User
                      |
                      v
                 AI Agent
                      |
                      v
                 messages[]
                      |
          -------------------------
          |           |           |
          v           v           v

    HumanMessage  AIMessage  ToolMessage

                      |
                      v
                  ChatOllama
                      |
                      v
                 Final Answer


Learning Goal:

Understand how an AI Agent maintains
conversation context using message history.

Important Message Types:

HumanMessage
    -> User input

AIMessage
    -> LLM response / tool request

ToolMessage
    -> Tool execution result


=====================================================
"""

from langchain_core.tools import tool

from langchain_ollama import ChatOllama

from langchain_core.messages import (
    HumanMessage,
    ToolMessage
)


# =====================================================
# Policy Database
# =====================================================

policy_database = {

    "accident": {

        "title": "Accident Reporting",

        "keywords": [
            "accident",
            "crash",
            "collision"
        ],

        "answer":
        "Accidents must be reported within 30 days."

    },

    "claim": {

        "title": "Claim Requirements",

        "keywords": [
            "claim",
            "documents",
            "requirements"
        ],

        "answer":
        "A claim requires policy number, accident details and vehicle information."

    },

    "renewal": {

        "title": "Policy Renewal",

        "keywords": [
            "renew",
            "renewal",
            "expiry"
        ],

        "answer":
        "Policy renewal should be completed before the expiry date."

    },

    "coverage": {

        "title": "Motor Coverage",

        "keywords": [
            "coverage",
            "cover",
            "benefit"
        ],

        "answer":
        "Motor Insurance covers accidental vehicle damage."

    }

}


# =====================================================
# Customer Database
# =====================================================

customer_database = {

    "CUST001": {

        "Name": "Senthil",

        "Policy": "Motor Insurance",

        "Status": "Active"

    },

    "CUST002": {

        "Name": "Ramesh",

        "Policy": "Travel Insurance",

        "Status": "Expired"

    }

}


# =====================================================
# Claim Database
# =====================================================

claim_database = {

    "CLM001": {

        "customer_id": "CUST001",

        "status": "Under Review",

        "amount": "RM 5000"

    },

    "CLM002": {

        "customer_id": "CUST002",

        "status": "Approved",

        "amount": "RM 8000"

    },

    "CLM003": {

        "customer_id": "CUST001",

        "status": "Rejected",

        "amount": "RM 3000"

    }

}


# =====================================================
# Tool 1: Search Policy
# =====================================================

@tool
def search_policy(question: str):
    """
    Search the company's official motor insurance policy.

    Use this tool for questions related to:
    - accident reporting
    - claims
    - renewal
    - coverage
    """

    question = question.lower()

    for policy in policy_database.values():

        for keyword in policy["keywords"]:

            if keyword in question:

                return policy["answer"]

    return "Policy information not found."


# =====================================================
# Tool 2: Get Customer Policy
# =====================================================

@tool
def get_customer_policy(customer_id: str):
    """
    Retrieve customer policy details.

    Use this tool when the user asks
    about customer policy information.
    """

    customer = customer_database.get(
        customer_id.upper()
    )

    if customer:

        return str(customer)

    return "Customer not found."


# =====================================================
# Tool 3: Check Claim Status
# =====================================================

@tool
def check_claim_status(claim_id: str):
    """
    Check insurance claim status.

    Use this tool when the user asks
    about claim status or claim progress.
    """

    claim = claim_database.get(
        claim_id.upper()
    )

    if claim:

        return str(claim)

    return "Claim not found."


# =====================================================
# Register Tools
# =====================================================

tools = [

    search_policy,

    get_customer_policy,

    check_claim_status

]


# =====================================================
# Tool Map
# =====================================================

tool_map = {

    tool.name: tool

    for tool in tools

}


# =====================================================
# Create LLM
# =====================================================

llm = ChatOllama(

    model="qwen2.5",

    temperature=0

)


# Bind tools to LLM

llm_with_tools = llm.bind_tools(
    tools
)


# =====================================================
# Conversation Memory
# =====================================================

messages = []


# =====================================================
# Agent Loop
# =====================================================

while True:

    print("\n" + "=" * 60)

    user_input = input(
        "You ('exit' to stop): "
    )


    # Exit condition

    if user_input.lower() in [
        "exit",
        "quit"
    ]:

        break


    # -------------------------------------------------
    # Add User Message to Memory
    # -------------------------------------------------

    messages.append(

        HumanMessage(
            content=user_input
        )

    )


    print("\nLLM Thinking...")


    # -------------------------------------------------
    # Ask LLM
    # -------------------------------------------------

    response = llm_with_tools.invoke(
        messages
    )


    # -------------------------------------------------
    # Add AI Response to Memory
    # -------------------------------------------------

    messages.append(
        response
    )


    # -------------------------------------------------
    # Check Tool Calls
    # -------------------------------------------------

    if response.tool_calls:

        print(
            f"\nTool Calls: "
            f"{len(response.tool_calls)}"
        )


        # -------------------------------------------------
        # Execute Tools
        # -------------------------------------------------

        for tool_call in response.tool_calls:

            print(
                "\nSelected Tool:",
                tool_call["name"]
            )

            print(
                "Arguments:",
                tool_call["args"]
            )


            selected_tool = tool_map[
                tool_call["name"]
            ]


            result = selected_tool.invoke(
                tool_call["args"]
            )


            print(
                "Tool Result:",
                result
            )


            # -------------------------------------------------
            # Add Tool Result to Memory
            # -------------------------------------------------

            messages.append(

                ToolMessage(

                    content=str(result),

                    tool_call_id=
                    tool_call["id"]

                )

            )


        # -------------------------------------------------
        # Ask LLM Again After Tool Result
        # -------------------------------------------------

        final_response = llm.invoke(
            messages
        )


        # Add final AI response to memory

        messages.append(
            final_response
        )


        print(
            "\nFinal Answer:"
        )

        print(
            final_response.content
        )


    else:

        print(
            "\nFinal Answer:"
        )

        print(
            response.content
        )


# =====================================================
# Display Conversation Memory
# =====================================================

print("\n" + "=" * 60)

print("Conversation Memory")

print("=" * 60)


for message in messages:

    print(
        "\nMessage Type:",
        type(message).__name__
    )

    print(
        "Content:",
        message.content
    )

#user input
#My customer ID is CUST001
#What policy do I have?
#What is my claim status?