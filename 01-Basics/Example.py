
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3:latest"
)

response = llm.invoke("hello")
print(response)