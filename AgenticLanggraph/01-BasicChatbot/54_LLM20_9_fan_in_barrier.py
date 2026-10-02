"""
===============================================================
LangGraph 20.9.2 - Fan-in Barrier with Delayed Worker
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates the fan-in synchronization point.

One worker is intentionally delayed by 2 seconds.

The final report should execute only after the worker phase
has completed and the worker results have been merged.

LEARNING GOAL
-------------
Understand:

    FAN-OUT
        ->
    WORKERS
        ->
    FAN-IN
        ->
    FINAL REPORT

===============================================================
"""

from typing import Annotated, TypedDict
import operator
import time

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# =============================================================
# 1. Worker state
# =============================================================

class ClaimWorkerState(TypedDict):
    claim_id: str
    claim_type: str
    amount: float


# =============================================================
# 2. Overall state
# =============================================================

class OverallState(TypedDict):
    claims: list[dict]

    results: Annotated[
        list[dict],
        operator.add
    ]

    report: str


# =============================================================
# 3. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):

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

    claim_id = state["claim_id"]

    print(
        f"\nWorker started: {claim_id}"
    )

    # ---------------------------------------------------------
    # Intentionally delay CLM003
    # ---------------------------------------------------------

    if claim_id == "CLM003":

        print(
            f"{claim_id} is intentionally delayed..."
        )

        time.sleep(2)

        print(
            f"{claim_id} delay completed."
        )

    else:

        print(
            f"{claim_id} completed immediately."
        )

    result = {
        "claim_id": claim_id,
        "claim_type": state["claim_type"],
        "amount": state["amount"],
        "status": "ANALYZED",
    }

    print(
        f"Worker finished: {claim_id}"
    )

    return {
        "results": [result]
    }


# =============================================================
# 5. Final report
# =============================================================

def final_report(state: OverallState):

    print(
        "\n>>> FINAL REPORT NODE STARTED <<<"
    )

    print(
        f"Results available: {len(state['results'])}"
    )

    report = (
        f"Processed "
        f"{len(state['results'])} claims."
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

builder.add_node(
    "claim_worker",
    claim_worker
)

builder.add_node(
    "final_report",
    final_report
)


# =============================================================
# 7. Fan-out
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 8. Fan-in -> Final Report
# =============================================================

builder.add_edge(
    "claim_worker",
    "final_report"
)


# =============================================================
# 9. Final report -> END
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
# 12. Execute
# =============================================================

print("=" * 60)
print("FAN-IN BARRIER DEMONSTRATION")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "results": [],
        "report": "",
    }
)


# =============================================================
# 13. Final state
# =============================================================

print("\n" + "=" * 60)
print("FINAL STATE")
print("=" * 60)

print(
    f"Results : {len(result['results'])}"
)

print(
    f"Report  : {result['report']}"
)