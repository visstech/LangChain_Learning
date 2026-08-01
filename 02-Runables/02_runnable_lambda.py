from langchain_core.runnables import RunnableLambda 
from langchain_ollama import ChatOllama 

def squre(number):
    return number * number

llm = ChatOllama(model="llama3:latest")

runable = RunnableLambda(squre)
result = runable.invoke(10)
print(result)

def clean_text(text):
    return text.strip().replace("\n", " ")

cleaner = RunnableLambda(clean_text)

cleaned_text = cleaner.invoke('This is my \n sample program and i am learning Langchain')
print(cleaned_text)