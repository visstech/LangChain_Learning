from typing import Any


from ctypes import py_object
from langchain_core.prompts import PromptTemplate 
from langchain_ollama import ChatOllama 
from pydantic import BaseModel,Field
from langchain_core.output_parsers import PydanticOutputParser 

class Person(BaseModel):
    name:str =Field(description="persons full name")
    age:int = Field(description="Person age")
    profession: str = Field(description="person's profession" )
    city:str = Field(description="City where the person work")


parser = PydanticOutputParser(
    pydantic_object=Person
)

llm = ChatOllama(
    model="llama3:latest",
    temperature=0

)

prompt = PromptTemplate(
    template="""

Extract person information from the text.

{format_instructions}

Text:
{text}

""",

    input_variables=[
        "text"
    ],

    partial_variables={
        "format_instructions":
        parser.get_format_instructions()
    }
)

chain = prompt | llm | parser

response = chain.invoke(
    {
        "text":
        """
        Senthil Kumar is 35 years old.
        He works as an AI Engineer in Kuala Lumpur.
        """
    }
)

print(response)