
# ReAct Agent Architecture

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode,tools_condition


from langchain_groq import ChatGroq

from dotenv import load_dotenv


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# 2. Define Graph State
# --------------------------------------------------

class State(TypedDict):

    # messages is a list of chat messages.
    #
    # add_messages tells LangGraph how to update
    # this state value.
    #
    # Instead of replacing the existing messages,
    # new messages are appended to the list.

    messages: Annotated[list, add_messages]


# --------------------------------------------------
# 3. Create Groq LLM
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)



graph_builder = StateGraph(State)


#custom function
def multiply(a:int,b:int)->int:
    """
    Multiply a and b
    args:
      a(int) -> first input
      b(int) -> second input 
      returns: int -> multiplied output
    """
    return a*b


tool= TavilySearch(max_results=2)
print(tool.invoke('What is langchain'))

tools =[tool,multiply]


llm_with_tools = llm.bind_tools(tools)

#Node definition
def tool_calling_llm(state:State):
    return {"messages":[llm_with_tools.invoke(state["messages"])]}
#add node
graph_builder.add_node('tool_calling_llm',tool_calling_llm)
graph_builder.add_node('tools',ToolNode(tools))

## Add Edges
graph_builder.add_edge(START, "tool_calling_llm")
graph_builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition
)
graph_builder.add_edge("tools",'tool_calling_llm')

## compile the graph
graph=graph_builder.compile()


# Display graph structure as Mermaid
png_data = graph.get_graph().draw_mermaid_png()

with open("langgraph.png", "wb") as f:
    f.write(png_data)

print("Graph saved as langgraph.png")
# --------------------------------------------------
# 10. Display Response
# --------------------------------------------------
response=graph.invoke({"messages":"What is the recent ai news and what is 5 multiply by 15"})

print(response["messages"][-1].content)

for m in response['messages']:
    print(m.pretty_print())