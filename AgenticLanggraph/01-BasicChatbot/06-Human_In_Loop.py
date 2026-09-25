'''1. What is Human-in-the-loop?

Human-in-the-loop means:

The AI agent pauses at an important decision and asks a human for approval
or input before continuing.

Instead of:
User → AI Agent → Tool → Action → Done

we have:
User
  ↓
AI Agent
  ↓
Decision
  ↓
⏸️ PAUSE
  ↓
👤 Human approval
  ↓
AI Agent
  ↓
Tool / Action
  ↓
Result


START
  ↓
AI decides
  ↓
Delete file?
  ↓
⏸️ HUMAN APPROVAL
  ↓
 ┌───────────────┐
 │               │
Approve        Reject
 │               │
 ↓               ↓
Delete          Stop
 │               │
 └──────→ END ←──┘
'''
from typing import TypedDict
from langgraph.graph import START,END,StateGraph
from langgraph.types import interrupt,Command
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
      message:str
      decision:str

def request_approval(state: State):

    decision = interrupt("Do you approve this action?")

    if decision == "YES":
        print("Action approved")
    else:
        print("Action rejected")
    return {
        "decision": decision
    }

builder = StateGraph(State)
builder.add_node('Approval',request_approval)
builder.add_edge(START,'Approval')
builder.add_edge('Approval',END)

memory = InMemorySaver()

graph = builder.compile(checkpointer=memory)


config = {
    "configurable": {
        "thread_id": "user-001"
    }
}

result = graph.invoke(
    {
        "message": "Please perform the action",
        "decision": ""
    },
    config
)

print(result)
print('Resume the graph with user approval')
graph.invoke(
    Command(resume="NO"),
    config
)