from langchain_core.prompts import PromptTemplate 
from langchain_ollama import ChatOllama 
from langchain_core.output_parsers import JsonOutputParser 

llm = ChatOllama(model="llama3:latest") 
parser = JsonOutputParser() 

prompt = PromptTemplate.from_template(
                            """
                            Extract the following information from the text.
                            RIMPORTANT RULES:
                            - Return ONLY valid JSON.
                            - Do not add explanations.
                            - Do not add markdown.
                            - Do not add ```.

                Required format:

                {{
                    "name": "string",
                    "age": number,
                    "policy_number": "string"
                }}
                                        Text:
                                        {text}
                                        """
                                    )
chain = prompt | llm | parser 

response = chain.invoke(
        {
        "text": "Senthilkumar sundaram is 35 years old and policy number is MT123456"
    }

)

print(response)
