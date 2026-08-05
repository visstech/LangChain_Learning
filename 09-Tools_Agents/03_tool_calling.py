from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

llm = ChatOllama(model="qwen2.5",
                temperature=0
                )

@tool
def add_numbers(a: int, b: int):
    """
    Add two numbers.

    Use this tool when the user
    wants addition.
    """

    return a + b



@tool
def multiply_numbers(a: int, b: int):
    """
    Multiply two numbers.

    Use this tool when the user
    wants multiplication.
    """

    return a * b



@tool
def divide_numbers(a: int, b: int):
    """
    Divide first number by second number.

    Use this tool when the user
    wants division.
    """

    return a / b

tools = [divide_numbers,add_numbers,multiply_numbers
        ]    

llm_with_tools = llm.bind_tools(tools)

question = HumanMessage(

    content="What is 25 multiplied by 10?"

)

response = llm_with_tools.invoke(

    [
        question
    ]

)


print(response)