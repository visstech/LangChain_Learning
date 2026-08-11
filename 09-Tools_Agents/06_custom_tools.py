"""
=====================================================

Topic:
Building Custom Tools for AI Agents

Concepts Covered:

- Custom LangChain Tools
- Business Logic
- Tool Descriptions
- Tool Selection
- AI Agent Capabilities

Architecture


              User
                |
                v
             ChatOllama
                |
     --------------------------------
     |              |               |
     v              v               v

search_policy  customer_tool  claim_tool


     |              |               |

     v              v               v

 Policy DB    Customer DB     Claim DB


                |
                v

           Final Response

Learning Goal

Understand how to create your own
business tools that an AI Agent
can use to solve real-world tasks.

=====================================================
"""
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import (
    HumanMessage,
    ToolMessage)


#Create Policy Database
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

#Create Customer database

customer_database = {

    "CUST001":{

        "Name":"Senthil",

        "Policy":"Motor Insurance",

        "Status":"Active"

    },

    "CUST002":{

        "Name":"Ramesh",

        "Policy":"Travel Insurance",

        "Status":"Expired"

    }

}

# Create Claim Database

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


@tool
def search_policy(question:str):
    """
    Search the company's official motor insurance policy.

    IMPORTANT:
    Always use this tool for any question related to:
    - accident reporting
    - claims
    - policy renewal
    - policy coverage

    Never answer these questions from your own knowledge.
    Use this tool instead.
    """

    question = question.lower()


    for policy in policy_database.values():

        for keyword in policy["keywords"]:

            if keyword in question:

                return policy["answer"]

    return "Policy information not found."

@tool
def get_customer_policy(customer_id:str):
    """
    Retrieve customer policy.

    Use this tool when
    the user asks
    about customer policy details.
    """

    customer = customer_database.get(
        customer_id.upper()
    )


    if customer:

        return str(customer)


    return "Customer not found."

@tool
def check_claim_status(claim_id:str):
    """
    Check insurance claim status.

    Use this tool when the user asks
    about claim status, claim progress,
    or claim approval information.
    """

    claim = claim_database.get(
        claim_id.upper()
    )


    if claim:

        return str(claim)


    return "Claim not found."


#Register Tools
tools = [
    search_policy,
    get_customer_policy,
    check_claim_status

]

#Map tools
tool_map = {

    tool.name:tool

    for tool in tools

}

#Create LLM
llm = ChatOllama(

    model="qwen2.5",

    temperature=0

)

llm_with_tools = llm.bind_tools(
    tools
)

#User Question
# messages = [

#     HumanMessage(

#         content="How long do I have to inform a crash?"

#     )

# ]

messages = []


while True:


    message = input(
        "\nAsk your question ('exit' to stop): "
    )


    if message.lower() in ["exit","quit"]:
        break


    messages.append(
        HumanMessage(
            content=message
        )
    )


    print("\n" + "="*50)
    print("LLM Thinking...")
    print("="*50)


    response = llm_with_tools.invoke(
        messages
    )


    messages.append(
        response
    )


    if response.tool_calls:


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

                    tool_call_id=tool_call["id"]

                )

            )


        # Ask LLM again after tool result

        final_response = llm.invoke(
            messages
        )


        print(
            "\nFinal Answer:"
        )

        print(
            final_response.content
        )


        messages.append(
            final_response
        )


    else:


        print(
            "\nFinal Answer:"
        )

        print(
            response.content
        )

        