from langchain_core.prompts import PromptTemplate 
from langchain_ollama import ChatOllama  
llm = ChatOllama(model="llama3:latest") 
prompt = PromptTemplate.from_template(
    "My name is  {name} and i am working as {job} in {company}"
)
response = llm.invoke(prompt.invoke({"name":"senthilkumar",
                                     "job":"AI Engineer",
                                     "company":"Visstech AI Solutions Pvt"}))
print(response.content)