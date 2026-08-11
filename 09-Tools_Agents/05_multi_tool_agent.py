"""
=====================================================

Topic:
Multi Tool AI Agent

Concepts Covered:
- Agent Loop
- Multiple Tool Calls
- Tool Execution
- Observation
- Reasoning Cycle

Architecture

User
   |
   ▼
LLM
   |
   ▼
Tool Call?
   |
Yes ▼     No ▼
Tool      Final Answer
   |
   ▼
Tool Result
   |
   ▼
LLM Again

Learning Goal

Understand that an AI Agent repeatedly:
1. Thinks
2. Chooses a tool
3. Executes it
4. Observes the result
5. Thinks again

until the task is complete.

=====================================================
"""

from langchain_core.tools import tool

from langchain_ollama import ChatOllama

from langchain_core.messages import (
    HumanMessage,
    ToolMessage
)

@tool
def add_numbers(a: int, b: int):
    """
    Add two numbers.

    Use this tool for addition.
    """

    return a + b



@tool
def multiply_numbers(a: int, b: int):
    """
    Multiply two numbers.

    Use this tool for multiplication.
    """

    return a * b



@tool
def divide_numbers(a: int, b: int):
    """
    Divide first number by second number.

    Use this tool for division.
    """

    return a / b

tools = [

    add_numbers,

    multiply_numbers,

    divide_numbers

]


tool_map = {

    tool.name: tool

    for tool in tools

}

llm = ChatOllama(

    model="qwen2.5",

    temperature=0

)

llm_with_tools = llm.bind_tools(
    tools
)

messages = [
    HumanMessage(
        content="Calculate (20 * 5) + 30"
    )
]

while True:

    print("\n" + "=" * 50)
    print("LLM Thinking...")
    print("=" * 50)

    response = llm_with_tools.invoke(messages)

    messages.append(response)

    if not response.tool_calls:
        print("\nNo more tool calls.")
        print("Agent has completed its reasoning.")
        break

    print(f"\nTool Calls: {len(response.tool_calls)}")


    # Execute tools here

    for tool_call in response.tool_calls:

        print("\nSelected Tool :", tool_call["name"])
        print("Arguments     :", tool_call["args"])

        selected_tool = tool_map[tool_call["name"]]

        result = selected_tool.invoke(tool_call["args"])

        print("Tool Result   :", result)

        messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )


print("\nFinal Answer:\n")

print(response.content)

"""
=====================================================

Key Learning:

A Multi Tool AI Agent follows:

1. Reason
2. Select Tool
3. Execute Tool
4. Observe Result
5. Reason Again

The loop continues until:

response.tool_calls == []

At that point the Agent generates
the final answer.


This is the foundation of:

- ReAct Agents
- LangGraph Workflows
- Autonomous AI Systems
=====================================================
"""