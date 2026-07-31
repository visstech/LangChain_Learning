from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_ollama import ChatOllama 

llm = ChatOllama(model="llama3:latest")
#A SystemMessage provides high-level instructions to the LLM, defining its role, 
# behavior, tone, constraints, and rules before processing any user request.
#HumanMessage
#A HumanMessage represents the user's input or question that the LLM needs to answer.
#AIMessage
#A AIMessage represents the model's response or answer.
messages =[SystemMessage(content=" You are a senior AI/ML mentor who teaches step by step, gives interview tips, and includes one practical example in every answer"),
HumanMessage(content="Explain what is the diffrence between supervised and unsupervised learning?")]
response = llm.invoke(messages)
print(response.content)