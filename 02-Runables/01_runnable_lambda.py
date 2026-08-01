from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def clean_text(text):
    return text.strip()

llm = ChatOllama(model='llama3:latest')

cleaner = RunnableLambda(clean_text)

prompt = ChatPromptTemplate.from_messages([("system",
                              "you are an experinced AI tutor"),
                            ("human",
                            "Explain me this {topic}")
                            ])
chain =cleaner | prompt | llm 

response = chain.invoke("    Randomforest classifier   ")
print(response.content)
