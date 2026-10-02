"""
===============================================================
LangGraph 20.9.3 - Parallel Worker Failure
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program intentionally causes one parallel worker to fail.

Workers:

    CLM001 -> SUCCESS
    CLM002 -> SUCCESS
    CLM003 -> FAILURE
    CLM004 -> SUCCESS

The goal is to observe what happens to the overall graph when
one worker raises an exception.

LEARNING GOAL
-------------
Understand the DEFAULT behavior of a parallel workflow when
one worker fails.

We are NOT adding retry or error handling yet.

Those concepts will come AFTER we understand the default
failure behavior.

IMPORTANT
---------
This is an intentional failure for learning.

Expected behavior:

    One worker raises an exception
        ->
    graph.invoke() raises an exception
        ->
    final_report should not be treated as successfully
    completed.

Later we will learn how to handle this safely using:

    - RetryPolicy
    - Error handlers
    - Fallback results
    - Partial-success patterns

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
    """
    FAN-OUT

    Create one Send object for each claim.
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
    Process one claim.

    CLM003 intentionally raises an exception.
    """

    claim_id = state["claim_id"]

    print(
        f"\nWorker started: {claim_id}"
    )

    # ---------------------------------------------------------
    # Intentional failure
    # ---------------------------------------------------------

    if claim_id == "CLM003":

        print(
            "❌ CLM003 is intentionally failing!"
        )

        raise ValueError(
            "Simulated processing failure for CLM003"
        )


    # ---------------------------------------------------------
    # Normal successful worker
    # ---------------------------------------------------------

    print(
        f"✅ {claim_id} processed successfully."
    )

    result = {
        "claim_id": claim_id,
        "claim_type": state["claim_type"],
        "amount": state["amount"],
        "status": "SUCCESS",
    }

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
        f"Results available: "
        f"{len(state['results'])}"
    )

    return {
        "report": (
            f"Processed "
            f"{len(state['results'])} claims."
        )
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
# 7. FAN-OUT
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 8. Workers -> Final report
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
# 12. Execute graph
# =============================================================

print("=" * 60)
print("PARALLEL WORKER FAILURE TEST")
print("=" * 60)

try:

    result = graph.invoke(
        {
            "claims": claims,
            "results": [],
            "report": "",
        }
    )

    print("\nGraph completed successfully.")

    print(
        f"Results: {len(result['results'])}"
    )

    print(
        f"Report : {result['report']}"
    )


except Exception as exc:

    print("\n" + "=" * 60)
    print("GRAPH EXECUTION FAILED")
    print("=" * 60)

    print(
        f"Exception type : {type(exc).__name__}"
    )

    print(
        f"Exception      : {exc}"
    )

    print(
        "\nThe failure was intentionally triggered by CLM003."
    )

    print(
        "Retry and error-handling strategies will be covered "
        "in later lessons."
    )