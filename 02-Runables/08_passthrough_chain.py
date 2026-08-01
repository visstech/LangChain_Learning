from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableParallel
)

def word_count(text):
    return len(text.split())

def character_count(text):
    return len(text)

word_counter = RunnableLambda(word_count)
character_counter = RunnableLambda(character_count)
chain = RunnableParallel(
    original_text=RunnablePassthrough(),
    word_count=word_counter ,
    character_count=character_counter
)

result = chain.invoke(
    "LangChain is powerful for building AI applications"
)

print(result)