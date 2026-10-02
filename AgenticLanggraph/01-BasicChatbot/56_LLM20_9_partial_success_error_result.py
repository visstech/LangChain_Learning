"""
===============================================================
LangGraph 20.9.4 - Partial Success + Error Result
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates partial success in a parallel
LangGraph workflow.

One worker intentionally fails.

Instead of allowing the exception to terminate the workflow,
the worker catches the exception and returns a structured
FAILED result.

LEARNING GOAL
-------------
Understand how a worker can convert:

    Exception
        ↓
    Error result
        ↓
    Reducer
        ↓
    Final report

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

    # ---------------------------------------------------------
    # Multiple workers update this key.
    # Reducer combines all lists.
    # ---------------------------------------------------------

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
    Create one dynamic worker branch for every claim.
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
# 4. Claim worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process one claim.

    CLM003 intentionally raises an error.

    The exception is caught inside the worker and converted
    into a FAILED result.
    """

    claim_id = state["claim_id"]

    print(
        f"\nWorker started: {claim_id}"
    )

    try:

        # -----------------------------------------------------
        # Simulated business processing
        # -----------------------------------------------------

        if claim_id == "CLM003":

            print(
                f"❌ Simulating failure for {claim_id}"
            )

            raise ValueError(
                "Simulated claim-processing failure"
            )

        # -----------------------------------------------------
        # Successful processing
        # -----------------------------------------------------

        print(
            f"✅ {claim_id} processed successfully."
        )

        result = {
            "claim_id": claim_id,
            "claim_type": state["claim_type"],
            "amount": state["amount"],
            "status": "SUCCESS",
            "error": None,
        }

        return {
            "results": [result]
        }

    except Exception as exc:

        # -----------------------------------------------------
        # Convert the exception into a structured result
        # -----------------------------------------------------

        print(
            f"⚠️ Error captured for {claim_id}: {exc}"
        )

        error_result = {
            "claim_id": claim_id,
            "claim_type": state["claim_type"],
            "amount": state["amount"],
            "status": "FAILED",
            "error": str(exc),
        }

        return {
            "results": [error_result]
        }


# =============================================================
# 5. Final report
# =============================================================

def final_report(state: OverallState):
    """
    Runs after the worker results have been aggregated.

    Produces a summary of successful and failed claims.
    """

    print(
        "\n>>> FINAL REPORT NODE STARTED <<<"
    )

    results = state["results"]

    success_count = sum(
        1
        for item in results
        if item["status"] == "SUCCESS"
    )

    failed_count = sum(
        1
        for item in results
        if item["status"] == "FAILED"
    )

    total_count = len(results)

    print(
        f"Total results   : {total_count}"
    )

    print(
        f"Successful      : {success_count}"
    )

    print(
        f"Failed          : {failed_count}"
    )

    report = (
        f"Processed {success_count} successfully "
        f"and {failed_count} failed "
        f"out of {total_count} claims."
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
# 7. FAN-OUT
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 8. FAN-IN -> Final report
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
# 11. Input claims
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
print("PARTIAL SUCCESS WORKFLOW")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "results": [],
        "report": "",
    }
)


# =============================================================
# 13. Display all results
# =============================================================

print("\n" + "=" * 60)
print("ALL CLAIM RESULTS")
print("=" * 60)

for item in result["results"]:

    print(
        f"\nClaim ID : {item['claim_id']}"
    )

    print(
        f"Status   : {item['status']}"
    )

    print(
        f"Error    : {item['error']}"
    )


# =============================================================
# 14. Final report
# =============================================================

print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)

print(
    result["report"]
)


# =============================================================
# 15. Workflow summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    "Failure handling : Exception -> FAILED result"
)

print(
    "Fan-out          : 1 -> Many"
)

print(
    "Fan-in           : Many -> 1"
)

print(
    "Reducer          : operator.add"
)