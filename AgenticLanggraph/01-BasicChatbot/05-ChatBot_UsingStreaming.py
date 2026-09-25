
# Streaming
#Methods: .stream() and astream()
#These methods are sync and async methods for streaming back results.
#Additional parameters in streaming modes for graph state

#values : This streams the full state of the graph after each node is called.
          #values gives the complete state after each step.
#updates : This streams updates to the state of the graph after each node is called.
           #gives you the state updates produced by graph nodes.
#messages: streams the LLM's generated message chunks/tokens.

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()


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



#Node definition
def streambot(state:State):
    return {"messages":[llm.invoke(state["messages"])]}
#add node
graph_builder.add_node('streambot',streambot)


## Add Edges
graph_builder.add_edge(START, "streambot")

graph_builder.add_edge("streambot",END)

## compile the graph
graph=graph_builder.compile(checkpointer=memory) #check pointer is used for memory


# Display graph structure as Mermaid
png_data = graph.get_graph().draw_mermaid_png()

with open("langgraph_Stream.png", "wb") as f:
    f.write(png_data)

print("Graph saved as langgraph_Stream.png")
# --------------------------------------------------
# 10. Display Response
# --------------------------------------------------


# Create a thread
config = {"configurable": {"thread_id": "2"}}

for chunk in graph.stream({'messages':"Hi,My name is Senthil And I like kabadi"},config,stream_mode="updates"):
    print(chunk)

# Create a thread
config = {"configurable": {"thread_id": "3"}}

for chunk in graph.stream({'messages':"Hi, I also like foodball"},config,stream_mode="values"):
    print(chunk)


config = {"configurable": {"thread_id": "4"}}

for chunk in graph.stream({'messages':"Hi, I also like foodball"},config,stream_mode="messages"):
    print(chunk)


config = {"configurable": {"thread_id": "5"}}
#astream 
    
async def stream_events():

    async for event in graph.astream_events(
        {
            "messages": [
                ("user", "Hi, I also like to listen to music")
            ]
        },
        config,
        version="v2"
    ):
        print(event)