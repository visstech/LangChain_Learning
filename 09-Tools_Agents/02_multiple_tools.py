from langchain_core.tools import tool

@tool
def add_numbers(a:int,b:int):
    """
    add two numbers
    use this tool 
    when user wants to add two numbers
    """
    return a + b

@tool
def multiply_numbers(a:int,b:int):
        """
        multiply two numbers
        use this tool 
        when user wants multiplication
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

tools = [add_numbers,
        multiply_numbers,
        divide_numbers]

if __name__ == "__main__":


    print(
        "Addition:",
        add_numbers.invoke(
            {
                "a": 10,
                "b": 20
            }
        )
    )


    print(
        "Multiplication:",
        multiply_numbers.invoke(
            {
                "a": 10,
                "b": 20
            }
        )
    )


    print(
        "Division:",
        divide_numbers.invoke(
            {
                "a": 100,
                "b": 5
            }
        )
    )