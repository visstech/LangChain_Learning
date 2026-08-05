"""
=====================================================

Topic:
Building First AI Agent with LangChain Tools

Concepts Covered:
- LangChain Tools
- Tool Binding
- ChatOllama
- Qwen2.5 Tool Calling
- Agent Execution Loop

Architecture:

User Question
      |
      v
     LLM
      |
      v
 Tool Selection
      |
      v
 Execute Tool
      |
      v
 Tool Result
      |
      v
 LLM Final Response


Learning Goal:

Understand how an AI Agent:
1. Receives a user question
2. Decides which tool is required
3. Executes the selected tool
4. Sends the result back to the LLM
5. Generates the final answer


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
        content="What is 25 multiplied by 10?"
    )

]

response = llm_with_tools.invoke(
    messages
)


messages.append(response)


for tool_call in response.tool_calls:

    selected_tool = tool_map[
        tool_call["name"]
    ]


    tool_result = selected_tool.invoke(
        tool_call["args"]
    )


    print(
        "Tool Result:",
        tool_result
    )


    messages.append(
        ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"]
        )
    )

final_response = llm.invoke(
    messages
)


print(
    "\nFinal Answer:"
)

print(
    final_response.content
)


"""
Agent Execution Loop:

1. User asks question
2. LLM decides required tool
3. Application executes tool
4. Tool result is returned to LLM
5. LLM generates final answer


The LLM is the brain.
Tools are the actions.
The Agent connects both.
"""