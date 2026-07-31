from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama:latest")
messages = [HumanMessage(content="Hi my name is senthil"),
            AIMessage(content="Hello Senthil, how can I help you today?"),
            HumanMessage(content="what is my name?" )]
response = llm.invoke(messages)
print(response.content) 