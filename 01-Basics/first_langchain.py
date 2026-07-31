from langchain_ollama import ChatOllama


# Connect LangChain with Ollama
llm = ChatOllama(
    model="llama3:latest"
)


# Send request
response = llm.invoke(
    "Explain Artificial Intelligence in simple words"
)


# Display answer
print(response.content)