
# Basic Chatbot using LangGraph (Graph API)

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_tavily import TavilySearch

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


# --------------------------------------------------
# 4. Define Chatbot Node
# --------------------------------------------------

def chatbot(state: State):

    return {
        "messages": [llm.invoke(state["messages"])]
    }


# --------------------------------------------------
# 5. Create StateGraph
# --------------------------------------------------

graph_builder = StateGraph(State)


# --------------------------------------------------
# 6. Add Node
# --------------------------------------------------

graph_builder.add_node(
    "llmchatbot",
    chatbot
)


# --------------------------------------------------
# 7. Add Edges
# --------------------------------------------------

graph_builder.add_edge(
    START,
    "llmchatbot"
)

graph_builder.add_edge(
    "llmchatbot",
    END
)


# --------------------------------------------------
# 8. Compile Graph
# --------------------------------------------------

graph = graph_builder.compile()


# --------------------------------------------------
# 9. Invoke Graph
# --------------------------------------------------

result = graph.invoke(
    {
        "messages": [
            ("user", "Hi")
        ]
    }
)

# Display graph structure as Mermaid
png_data = graph.get_graph().draw_mermaid_png()

with open("langgraph.png", "wb") as f:
    f.write(png_data)

print("Graph saved as langgraph.png")
# --------------------------------------------------
# 10. Display Response
# --------------------------------------------------

print(result["messages"]) # [-1].content for display only llm response.
print(result["messages"][-1].content)


tool= TavilySearch(max_results=2)
tool.invoke('What is langchain')
