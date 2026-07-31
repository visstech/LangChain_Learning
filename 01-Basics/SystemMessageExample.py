from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3:latest")
messages =[SystemMessage(content="You are interviewing a candidate for an AI Engineer position."),
HumanMessage(content="Ask me five langchain interview questions.")]
response = llm.invoke(messages)
print(response.content)