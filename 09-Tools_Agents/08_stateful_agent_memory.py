from email import message
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from langchain_ollama import ChatOllama
from langchain.tools import tool



agent_state = {

    "customer_id": None,

    "messages": []
}

@tool
def get_customer_claims(customer_id: str):
    """
    Retrieve all claims for a customer.
    Use this tool when customer asks about
    claim status without providing claim id.
    """

    customer_claims = {

        "CUST001": [

            {
                "claim_id": "CLM001",
                "status": "Under Review",
                "amount": "RM 5000"
            },

            {
                "claim_id": "CLM003",
                "status": "Rejected",
                "amount": "RM 3000"
            }

        ],

        "CUST002": [

            {
                "claim_id": "CLM002",
                "status": "Approved",
                "amount": "RM 8000"
            }

        ]

    }


    return str(
        customer_claims.get(
            customer_id.upper(),
            "No claims found"
        )
    )

tools =[get_customer_claims]
tool_map = {

    tool.name: tool

    for tool in tools

}


llm = ChatOllama(model="qwen2.5",
    temperature=0)

llm_with_tools = llm.bind_tools(
    tools
)




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

