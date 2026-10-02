"""
===============================================================
LangGraph 20.8.5 - Multiple Workers Without a Reducer
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates what happens when multiple parallel
workers try to update the SAME state field without defining
a reducer.

The workflow is:

    Input
      ↓
    Dispatcher
      ↓
    Multiple Workers
      ↓
    All workers update "results"

LEARNING GOAL
-------------
Understand WHY reducers are required when multiple parallel
branches write to the same state field.

COMPARE WITH
------------
46_LLM20_8_fanout_fanin.py

In that program we used:

    Annotated[list[str], operator.add]

Here we intentionally REMOVE the reducer.

IMPORTANT
---------
This is a learning experiment.

The purpose is to observe LangGraph's state-update behavior
when concurrent branches target the same field.

===============================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# =============================================================
# 1. State WITHOUT reducer
# =============================================================

class OverallState(TypedDict):
    claims: list[dict]

    # No reducer here.
    results: list[str]


# =============================================================
# 2. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        print(
            f"Creating worker for {claim['claim_id']}"
        )

        sends.append(
            Send(
                "claim_worker",
                {
                    "claim_id": claim["claim_id"]
                }
            )
        )

    return sends


# =============================================================
# 3. Worker
# =============================================================

def claim_worker(state):

    claim_id = state["claim_id"]

    print(
        f"Worker processing: {claim_id}"
    )

    return {
        "results": [
            f"{claim_id} processed"
        ]
    }


# =============================================================
# 4. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)

builder.add_node(
    "claim_worker",
    claim_worker
)

builder.add_conditional_edges(
    START,
    dispatch_claims
)

builder.add_edge(
    "claim_worker",
    END
)


# =============================================================
# 5. Compile
# =============================================================

graph = builder.compile()


# =============================================================
# 6. Input
# =============================================================

claims = [
    {
        "claim_id": "CLM001"
    },
    {
        "claim_id": "CLM002"
    },
    {
        "claim_id": "CLM003"
    },
]


# =============================================================
# 7. Run
# =============================================================

print("=" * 60)
print("TESTING WITHOUT REDUCER")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "results": [],
    }
)

print("\nFinal State:")
print(result)