"""
===============================================================
LangGraph 20.8.3 - Send with Custom Worker State
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates how Send can provide DIFFERENT
state to each worker execution.

Each claim contains:

    claim_id
    claim_type
    amount

The dispatcher creates one Send object per claim and passes
that claim's own data to the worker.

EXAMPLE
-------
CLM001 -> Motor  -> RM 5000
CLM002 -> Health -> RM 12000
CLM003 -> Travel -> RM 3000

LEARNING GOAL
-------------
Understand that Send does not have to pass the same state
to every worker.

Each worker can receive its own custom input.

===============================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# =============================================================
# 1. Overall graph state
# =============================================================

class OverallState(TypedDict):
    claims: list[dict]


# =============================================================
# 2. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    Create one Send object for each claim.

    Each Send receives custom state for that claim.
    """

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        print(
            f"Creating task for {claim['claim_id']}"
        )

        sends.append(
            Send(
                "claim_worker",
                {
                    "claim_id": claim["claim_id"],
                    "claim_type": claim["claim_type"],
                    "amount": claim["amount"],
                }
            )
        )

    return sends


# =============================================================
# 3. Worker
# =============================================================

def claim_worker(state):
    """
    Process one claim.

    Each worker receives its own custom state.
    """

    print(
        f"Worker processing: "
        f"{state['claim_id']}"
    )

    print(
        f"  Type   : {state['claim_type']}"
    )

    print(
        f"  Amount : RM {state['amount']}"
    )

    return {}


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
# 6. Input claims
# =============================================================

claims = [
    {
        "claim_id": "CLM001",
        "claim_type": "Motor",
        "amount": 5000,
    },
    {
        "claim_id": "CLM002",
        "claim_type": "Health",
        "amount": 12000,
    },
    {
        "claim_id": "CLM003",
        "claim_type": "Travel",
        "amount": 3000,
    },
]


# =============================================================
# 7. Run workflow
# =============================================================

print("=" * 60)
print("STARTING CUSTOM WORKER STATE EXAMPLE")
print("=" * 60)

graph.invoke(
    {
        "claims": claims
    }
)


# =============================================================
# 8. Completion
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW COMPLETED")
print("=" * 60)

print(
    f"{len(claims)} claims were dynamically dispatched."
)