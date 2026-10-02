"""
===============================================================
LangGraph 20.8.1 - Send and Dynamic Parallelism
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates the LangGraph Send API.

The workflow:

    START
      ↓
    Dispatcher
      ↓
    Send multiple tasks
      ↓
    Worker node
      ↓
    END

The dispatcher dynamically creates one Send object for
each task in the input list.

Example:

    tasks = [
        "Policy",
        "Claims",
        "Customer"
    ]

The dispatcher creates:

    Send("worker", {"task": "Policy"})
    Send("worker", {"task": "Claims"})
    Send("worker", {"task": "Customer"})

LEARNING GOAL
-------------
Understand:

    Send
      +
    Dynamic task creation
      +
    Multiple executions of the same worker node

IMPORTANT
---------
This first lesson focuses only on dynamic dispatch.

We are NOT aggregating worker results yet.

Result aggregation and reducers will be studied later.

===============================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# =============================================================
# 1. Define graph state
# =============================================================

class OverallState(TypedDict):
    tasks: list[str]


# =============================================================
# 2. Dispatcher function
# =============================================================

def dispatch_tasks(state: OverallState):
    """
    Create one Send object for each task.

    The same worker node will be invoked multiple times.
    """

    print("\nDispatcher started.")

    print(
        f"Number of tasks: {len(state['tasks'])}"
    )

    sends = []

    for task in state["tasks"]:

        print(
            f"Creating Send for: {task}"
        )

        sends.append(
            Send(
                "worker",
                {
                    "task": task
                }
            )
        )

    return sends


# =============================================================
# 3. Worker node
# =============================================================

def worker(state):
    """
    Process one dynamically assigned task.

    Each Send invocation supplies its own task.
    """

    task = state["task"]

    print(
        f"Worker processing: {task}"
    )

    return {}


# =============================================================
# 4. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)


# Add worker node.
builder.add_node(
    "worker",
    worker
)


# =============================================================
# 5. Dynamic dispatch
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_tasks
)


# Each worker execution finishes the workflow branch.
builder.add_edge(
    "worker",
    END
)


# =============================================================
# 6. Compile graph
# =============================================================

graph = builder.compile()


# =============================================================
# 7. Run workflow
# =============================================================

print("=" * 60)
print("STARTING DYNAMIC PARALLEL WORKFLOW")
print("=" * 60)

graph.invoke(
    {
        "tasks": [
            "Policy Analysis",
            "Claims Analysis",
            "Customer Analysis"
        ]
    }
)


# =============================================================
# 8. Final message
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW COMPLETED")
print("=" * 60)

print(
    "All dynamically dispatched tasks were processed."
)