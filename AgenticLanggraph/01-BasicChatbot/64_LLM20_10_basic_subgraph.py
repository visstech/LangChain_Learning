"""
============================================================
64.1 - BASIC LANGGRAPH SUBGRAPH
============================================================

WHAT THIS PROGRAM DOES
----------------------
This program demonstrates the basic concept of a LangGraph
subgraph.

We create two separate graphs:

1. CHILD GRAPH
   - Performs a small piece of work.
   - Contains its own nodes and edges.

2. PARENT GRAPH
   - Represents the main workflow.
   - Calls the child graph as one step.
   - Receives the result from the child graph.

The purpose is to understand how a smaller LangGraph workflow
can be embedded inside a larger LangGraph workflow.

------------------------------------------------------------
WHY SUBGRAPHS ARE IMPORTANT
------------------------------------------------------------

As applications become larger, putting every node into one
large graph becomes difficult to maintain.

For example, an Insurance AI Agent might eventually contain:

    Authentication
          |
          v
    Intent Detection
          |
       +--+--+
       |     |
       v     v
    Policy  Claims
    Graph   Graph
       |     |
       +--+--+
          |
          v
       Response

Policy and Claims can each be implemented as separate
subgraphs.

This gives us:

    Parent Graph
        |
        +---- Authentication
        |
        +---- Policy Subgraph
        |
        +---- Claims Subgraph
        |
        +---- Final Response

------------------------------------------------------------
KEY CONCEPTS
------------------------------------------------------------

1. State
   Each graph has state.

2. Node
   A function that performs work on the state.

3. Edge
   Defines the execution flow.

4. Subgraph
   A compiled LangGraph graph used inside another graph.

5. Parent Graph
   The main workflow that uses the subgraph.

------------------------------------------------------------
EXPECTED FLOW
------------------------------------------------------------

START
  |
  v
Parent: prepare
  |
  v
Child Subgraph
  |
  +--> Child: process
  |
  +--> Child: finish
  |
  v
Parent: finalize
  |
  v
END

------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

This is intentionally a simple example.

We are NOT introducing:

- Persistence
- Checkpoints
- HITL
- Send
- Parallel processing
- RetryPolicy
- Tools
- Agents

Those will be introduced separately after we understand
the basic subgraph mechanism.
============================================================
A subgraph is a graph inside a larger graph, allowing us to modularize complex workflows.
"""


from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. CHILD GRAPH STATE
# ============================================================

class ChildState(TypedDict):
    message: str


# ============================================================
# 2. CHILD GRAPH NODES
# ============================================================

def child_process(state: ChildState):
    """
    Process the message inside the child graph.
    """

    print("Child Graph: processing...")

    return {
        "message": state["message"] + " -> processed by child"
    }


def child_finish(state: ChildState):
    """
    Final node of the child graph.
    """

    print("Child Graph: finishing...")

    return {
        "message": state["message"] + " -> child completed"
    }


# ============================================================
# 3. BUILD CHILD GRAPH
# ============================================================

child_builder = StateGraph(ChildState)

child_builder.add_node("child_process", child_process)
child_builder.add_node("child_finish", child_finish)

child_builder.add_edge(START, "child_process")
child_builder.add_edge("child_process", "child_finish")
child_builder.add_edge("child_finish", END)

child_graph = child_builder.compile()


# ============================================================
# 4. PARENT GRAPH STATE
# ============================================================

class ParentState(TypedDict):
    message: str


# ============================================================
# 5. PARENT GRAPH NODE - BEFORE SUBGRAPH
# ============================================================

def parent_prepare(state: ParentState):
    """
    Prepare the input before calling the child graph.
    """

    print("Parent Graph: preparing...")

    return {
        "message": state["message"] + " -> prepared by parent"
    }


# ============================================================
# 6. PARENT GRAPH NODE - CALL CHILD SUBGRAPH
# ============================================================

def call_child_graph(state: ParentState):
    """
    Execute the child graph.

    The parent sends its current state to the child graph.

    The child graph processes the state and returns its
    updated state.

    We then return that result to the parent graph.
    """

    print("Parent Graph: calling child subgraph...")

    child_result = child_graph.invoke(
        {
            "message": state["message"]
        }
    )

    return {
        "message": child_result["message"]
    }


# ============================================================
# 7. PARENT GRAPH NODE - AFTER SUBGRAPH
# ============================================================

def parent_finalize(state: ParentState):
    """
    Continue processing after the child graph completes.
    """

    print("Parent Graph: finalizing...")

    return {
        "message": state["message"] + " -> finalized by parent"
    }


# ============================================================
# 8. BUILD PARENT GRAPH
# ============================================================

parent_builder = StateGraph(ParentState)

parent_builder.add_node("parent_prepare", parent_prepare)
parent_builder.add_node("call_child", call_child_graph)
parent_builder.add_node("parent_finalize", parent_finalize)

parent_builder.add_edge(START, "parent_prepare")
parent_builder.add_edge("parent_prepare", "call_child")
parent_builder.add_edge("call_child", "parent_finalize")
parent_builder.add_edge("parent_finalize", END)

parent_graph = parent_builder.compile()


# ============================================================
# 9. RUN THE PARENT GRAPH
# ============================================================

print()
print("=" * 60)
print("64.1 - BASIC LANGGRAPH SUBGRAPH")
print("=" * 60)

result = parent_graph.invoke(
    {
        "message": "Insurance Claim"
    }
)


# ============================================================
# 10. DISPLAY FINAL RESULT
# ============================================================

print()
print("=" * 60)
print("FINAL RESULT")
print("=" * 60)

print(result)

print()
print("=" * 60)
print("GRAPH COMPLETED")
print("=" * 60)