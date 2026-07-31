from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama 
llm = ChatOllama(model="llama3:latest")
prompt = PromptTemplate.from_template(
    "Explain  {topic} in a simple manner?"
)
response = llm.invoke(prompt.invoke({"topic":"Machine leanring"}))
print(response.content)