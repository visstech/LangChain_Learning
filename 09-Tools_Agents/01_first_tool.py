from langchain_core.tools import tool
from pydantic.v1.networks import multi_host_url_regex

@tool
def multiply_number(a:int,b:int):
    """
    Multiply two numbers.

    Use this tool when the user
    wants multiplication.
    """
    return a * b 

result = multiply_number.invoke({
    "a":10,
    "b":25
})    

print(f'Mupltiplication result is:{result}')