"""
===============================================================
LangGraph 20.8.2 - Dynamic Send from Input Data
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates dynamic task creation using Send.

The input contains a list of items.

The dispatcher creates ONE Send object for EACH item.

Example:

    Input:
        ["Claim-001", "Claim-002", "Claim-003"]

    Dispatcher:
        Send -> Claim-001
        Send -> Claim-002
        Send -> Claim-003

The number of worker executions is determined entirely by
the input list.

LEARNING GOAL
-------------
Understand that:

    Number of input items
            ↓
    Number of Send objects
            ↓
    Number of worker executions

IMPORTANT
---------
We are still NOT aggregating the worker results.

That will be covered later with fan-in and reducers.

===============================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# =============================================================
# 1. Overall graph state
# =============================================================

class OverallState(TypedDict):
    claims: list[str]


# =============================================================
# 2. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    Create one Send object for every claim.
    """

    print("\nDispatcher started.")

    claims = state["claims"]

    print(
        f"Total claims received: {len(claims)}"
    )

    sends = []

    for claim in claims:

        print(
            f"Creating worker task for: {claim}"
        )

        sends.append(
            Send(
                "claim_worker",
                {
                    "claim_id": claim
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

    Each worker receives one claim_id from its Send object.
    """

    claim_id = state["claim_id"]

    print(
        f"Worker processing: {claim_id}"
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


# =============================================================
# 5. Dynamic fan-out
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


builder.add_edge(
    "claim_worker",
    END
)


# =============================================================
# 6. Compile
# =============================================================

graph = builder.compile()


# =============================================================
# 7. Input data
# =============================================================

claims = [
    "CLM001",
    "CLM002",
    "CLM003",
    "CLM004",
    "CLM005",
]


# =============================================================
# 8. Run workflow
# =============================================================

print("=" * 60)
print("STARTING DYNAMIC CLAIM PROCESSING")
print("=" * 60)

graph.invoke(
    {
        "claims": claims
    }
)


# =============================================================
# 9. Completion
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW COMPLETED")
print("=" * 60)

print(
    f"{len(claims)} claims were dynamically dispatched."
)