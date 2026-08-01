
from langchain_core.runnables import RunnableLambda 

def make_upper(text):
    return text.upper()

uppercase_runnable = RunnableLambda(make_upper)

result = uppercase_runnable.invoke("i am senthilkumar and i am leraning Langchain runableLamda")
print(result)

def add_exclamation(text):
    return  f'{text} !!!'

exclamation_runnable  = RunnableLambda(add_exclamation)
result = exclamation_runnable.invoke('This coding is excellent')
print(result)
 
chain = uppercase_runnable | exclamation_runnable #combine both functions

'''Connects multiple Runnable components in a fixed order 
where each component receives the output from the previous component.
chain = step1 | step2 | step3
chain = prompt | llm | parser
'''

response = chain.invoke('Learning langchain with help of Chargpt is great experience')

print(response)