"""
=====================================================

Topic:
AI Agent with PostgreSQL Long-Term Memory

Concepts Covered:

- LangChain Tools
- ChatOllama
- Tool Calling
- PostgreSQL
- MemoryManager
- Long-Term Memory

Architecture:

User
  |
  v
LLM
  |
  v
save_user_memory()
  |
  v
MemoryManager
  |
  v
PostgreSQL

Learning Goal:

Understand how an AI Agent can use
a custom memory tool to save information
into PostgreSQL.

=====================================================
"""

from langchain_core.tools import tool

from langchain_ollama import ChatOllama

from langchain_core.messages import (
    HumanMessage,
    ToolMessage
)

from memory.memory_manager import MemoryManager
from authorization import authorize_customer_access
from session import Session


# =====================================================
# Create Memory Manager
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


memory = MemoryManager(

    host="localhost",

    port=5432,

    database="insurance_ai",

    user="postgres",

    password="postgres123"

)


# =====================================================
# Memory Tool
# =====================================================

@tool
def save_user_memory(
    user_id: str,
    memory_key: str,
    memory_value: str
):
    """
    Save important user information
    into long-term memory.

    Use this tool when the user provides
    information that should be remembered
    for future conversations.
    """

    memory.save_memory(

        user_id=user_id,

        memory_key=memory_key,

        memory_value=memory_value,

        memory_type="user",

        importance=8

    )

    return "Memory saved successfully."

@tool
def get_user_memory(
    user_id: str,
    memory_key: str
):
    """
    Retrieve information from the user's
    long-term memory.

    Use this tool when the user asks about
    information that may have been remembered
    from an earlier interaction.
    """

    result = memory.get_memory(

        user_id=user_id,

        memory_key=memory_key

    )

    if result:

        return result

    return "Memory not found."

@tool
def get_my_policy():
    """
    Retrieve the authenticated customer's insurance policy
    """
    

    authenticated_user_id = session.get_user_id()

    allowed = authorize_customer_access(
        authenticated_user_id,
        authenticated_user_id
    )

    if not allowed:

        return "Access denied."

    customer = customer_database.get(
        authenticated_user_id.upper()
    )

    if customer:

        return str(customer)

    return "Customer not found."

@tool
def get_my_claims():
    """
    Retrieve all claims belonging to the
    authenticated customer.

    Use this tool when the user asks:
    - What are my claims?
    - Show my claims
    - What claims do I have?
    - What is my claim history?
    """

    authenticated_user_id = session.get_user_id()

    claims = []

    for claim_id, claim in claim_database.items():

        if claim["customer_id"] == authenticated_user_id:

            claims.append({
                "claim_id": claim_id,
                "status": claim["status"],
                "amount": claim["amount"]
            })

    if claims:

        return str(claims)

    return "No claims found."


@tool
def check_claim_status(claim_id: str):
    """
    Check the status of a claim belonging to
    the authenticated customer.

    Use this tool when the user asks about
    the status or progress of a specific claim.
    """

    authenticated_user_id = (
        session.get_user_id()
    )

    claim = claim_database.get(
        claim_id.upper()
    )

    if not claim:

        return "Claim not found."

    # Authorization check
    if (
        claim["customer_id"].upper()
        != authenticated_user_id.upper()
    ):

        return "You are not authorized to access this claim."

    return str({

        "claim_id": claim_id.upper(),

        "status": claim["status"],

        "amount": claim["amount"]

    })

# =====================================================
# Register Tools
# =====================================================

tools = [

    save_user_memory,
    get_user_memory,
    get_my_policy,
    get_my_claims,
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

customer_id = input(
    "Login - Customer ID: "
)

session = Session(customer_id)

print(
    "\nLogged in as:",
    session.get_user_id()
)

llm_with_tools = llm.bind_tools(
    tools
)


# =====================================================
# User Message
# =====================================================
messages = []
while True:

    print("\n" + "=" * 50)

    message = input(
        "You ('exit' to stop): "
    )

    if message.lower() == "exit":

        break


    messages.append(
        HumanMessage(
            content=message
        )
    )


    while True:

        print(
            "\nLLM Thinking..."
        )


        response = llm_with_tools.invoke(
            messages
        )


        messages.append(
            response
        )


        if not response.tool_calls:

            print(
                "\nFinal Answer:"
            )

            print(
                response.content
            )

            break


        print(
            "\nTool Calls:",
            len(response.tool_calls)
        )


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


            messages.append(

                ToolMessage(

                    content=str(result),

                    tool_call_id=
                    tool_call["id"]

                )

            )

# =====================================================
# Close Database
# =====================================================

memory.close()