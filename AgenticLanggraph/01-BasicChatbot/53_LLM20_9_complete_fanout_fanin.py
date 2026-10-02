"""
===============================================================
LangGraph 20.9.1 - Complete Fan-out / Fan-in Architecture
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program builds a complete parallel workflow.

Stages:

    Dispatcher
        ↓
    Dynamic Send
        ↓
    Parallel Workers
        ↓
    Reducer / Fan-in
        ↓
    Final Report
        ↓
    END

LEARNING GOAL
-------------
Understand the complete:

    1 -> Many -> 1

architecture.

===============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# =============================================================
# 1. Worker input state
# =============================================================

class ClaimWorkerState(TypedDict):
    claim_id: str
    claim_type: str
    amount: float


# =============================================================
# 2. Overall graph state
# =============================================================

class OverallState(TypedDict):

    # Original input
    claims: list[dict]

    # ---------------------------------------------------------
    # Reducer
    #
    # Multiple workers update "results".
    #
    # operator.add combines the lists.
    # ---------------------------------------------------------

    results: Annotated[
        list[dict],
        operator.add
    ]

    # Final report generated after fan-in
    report: str


# =============================================================
# 3. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    FAN-OUT

    Create one Send object for every claim.

    Each Send provides custom state to the worker.
    """

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        print(
            f"Creating Send for {claim['claim_id']}"
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

    print(
        f"Total worker branches: {len(sends)}"
    )

    return sends


# =============================================================
# 4. Worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process one claim independently.

    Each worker returns one result.

    The reducer combines all results.
    """

    claim_id = state["claim_id"]
    claim_type = state["claim_type"]
    amount = state["amount"]

    print(
        f"\nWorker processing {claim_id}"
    )

    result = {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "amount": amount,
        "status": "ANALYZED",
    }

    return {
        "results": [result]
    }


# =============================================================
# 5. Final report node
# =============================================================

def final_report(state: OverallState):
    """
    FAN-IN / FINALIZATION

    This node runs after the worker phase and receives the
    aggregated results.

    It creates one final summary.
    """

    print("\nFinal report node started.")

    total_claims = len(state["claims"])
    total_results = len(state["results"])

    report = (
        f"Processed {total_results} of "
        f"{total_claims} claims successfully."
    )

    print(
        f"Total input claims : {total_claims}"
    )

    print(
        f"Aggregated results : {total_results}"
    )

    return {
        "report": report
    }


# =============================================================
# 6. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)


# Register nodes
builder.add_node(
    "claim_worker",
    claim_worker
)

builder.add_node(
    "final_report",
    final_report
)


# =============================================================
# 7. START -> Dispatcher
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 8. Workers -> Final Report
# =============================================================

builder.add_edge(
    "claim_worker",
    "final_report"
)


# =============================================================
# 9. Final Report -> END
# =============================================================

builder.add_edge(
    "final_report",
    END
)


# =============================================================
# 10. Compile
# =============================================================

graph = builder.compile()


# =============================================================
# 11. Input
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
        "amount": 8000,
    },

    {
        "claim_id": "CLM003",
        "claim_type": "Travel",
        "amount": 12000,
    },

    {
        "claim_id": "CLM004",
        "claim_type": "Motor",
        "amount": 4500,
    },
]


# =============================================================
# 12. Run workflow
# =============================================================

print("=" * 60)
print("COMPLETE FAN-OUT / FAN-IN WORKFLOW")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "results": [],
        "report": "",
    }
)


# =============================================================
# 13. Display aggregated results
# =============================================================

print("\n" + "=" * 60)
print("AGGREGATED RESULTS")
print("=" * 60)

for item in result["results"]:

    print(
        f"{item['claim_id']} | "
        f"{item['claim_type']} | "
        f"RM {item['amount']} | "
        f"{item['status']}"
    )


# =============================================================
# 14. Display final report
# =============================================================

print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)

print(
    result["report"]
)


# =============================================================
# 15. Final summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    "Fan-out : Dispatcher -> multiple workers"
)

print(
    "Fan-in  : Worker results -> final_report"
)

print(
    "Reducer : operator.add"
)

print(
    "Pattern : 1 -> Many -> 1"
)