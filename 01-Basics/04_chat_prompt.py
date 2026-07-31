from langchain_core.prompts import ChatPromptTemplate 
from langchain_ollama import ChatOllama 
from langchain_core.output_parsers import PydanticOutputParser 
from langchain_core.messages import SystemMessage,HumanMessage

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert AI tutor. Explain concepts simply with examples."
        ),
        (
            "human",
            "Explain {topic}"
        )
    ]
)
llm = ChatOllama(model="llama3:latest")

chain = prompt | llm 
response = chain.invoke(
    {"topic":"Deep Learning"}
    )

print(response)