from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3:latest")

response = llm.invoke("Hello")

print(type(response))
print(response)
print(response.content)