from langchain_core.prompts import PromptTemplate 
from langchain_ollama import ChatOllama 
from langchain_core.output_parsers import StrOutputParser 

'''LCEL (LangChain Expression Language) is a declarative 
way to compose LangChain components using the pipe (|) operator. 
It allows developers to create reusable chains by connecting prompts,
 models, retrievers, and output parsers together.'''

llm = ChatOllama(model="llama3:latest")

prompt = PromptTemplate.from_template(
                        """
                        Explain {topic} in simple words.
                        Provide a real-world example.
                        Explain step by step.
                        """
                    )

parser = StrOutputParser() #converts outpus as string instead of object

chain = prompt | llm | parser

response = chain.invoke({"topic":"transformers in machine learning"})
print(response)

# Note Before LCEL:
# print(response.content)
#Ater LCEL
# print(response)

'''The parser already converted:

    AIMessage
        |
        v
    String'''