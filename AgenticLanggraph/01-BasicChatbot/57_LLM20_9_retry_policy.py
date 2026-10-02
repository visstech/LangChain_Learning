"""
===============================================================
LangGraph 20.9.5 - Native RetryPolicy
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates LangGraph's built-in RetryPolicy.

CLM003 intentionally fails on its first attempt.

LangGraph should automatically retry the worker.

On the second attempt, CLM003 succeeds.

LEARNING GOAL
-------------
Understand:

    Node failure
        ↓
    RetryPolicy
        ↓
    Retry
        ↓
    Successful execution

===============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy


# =============================================================
# 1. Worker state
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
# 3. Track attempts for learning demonstration
# =============================================================

attempts: dict[str, int] = {}


# =============================================================
# 4. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    Create one worker branch for each claim.
    """

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        claim_id = claim["claim_id"]

        print(
            f"Creating Send for {claim_id}"
        )

        sends.append(
            Send(
                "claim_worker",
                {
                    "claim_id": claim_id,
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
# 5. Worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process one claim.

    CLM003 intentionally fails on its first attempt.

    IMPORTANT:
    We do NOT catch the exception here.

    LangGraph RetryPolicy must see the exception so it can
    perform the retry.
    """

    claim_id = state["claim_id"]

    # ---------------------------------------------------------
    # Track current attempt
    # ---------------------------------------------------------

    attempts[claim_id] = (
        attempts.get(claim_id, 0) + 1
    )

    current_attempt = attempts[claim_id]

    print(
        f"\nWorker: {claim_id}"
    )

    print(
        f"Attempt: {current_attempt}"
    )


    # ---------------------------------------------------------
    # Intentional first-attempt failure
    # ---------------------------------------------------------

    if (
        claim_id == "CLM003"
        and current_attempt == 1
    ):

        print(
            "❌ CLM003 failing intentionally "
            "on first attempt."
        )

        raise ValueError(
            "Temporary processing failure"
        )


    # ---------------------------------------------------------
    # Success
    # ---------------------------------------------------------

    print(
        f"✅ {claim_id} succeeded."
    )

    result = {
        "claim_id": claim_id,
        "claim_type": state["claim_type"],
        "amount": state["amount"],
        "status": "SUCCESS",
        "attempt": current_attempt,
    }

    return {
        "results": [result]
    }


# =============================================================
# 6. Final report
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
            f"Successfully processed "
            f"{len(state['results'])} claims."
        )
    }


# =============================================================
# 7. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)


# =============================================================
# 8. Add worker with RetryPolicy
# =============================================================

builder.add_node(
    "claim_worker",
    claim_worker,
    retry_policy=RetryPolicy(
        initial_interval=0.1,
        backoff_factor=1.0,
        max_interval=0.1,
        max_attempts=2,
        jitter=False,
        retry_on=ValueError,
    ),
)


# =============================================================
# 9. Add final report node
# =============================================================

builder.add_node(
    "final_report",
    final_report
)


# =============================================================
# 10. Fan-out
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 11. Workers -> final report
# =============================================================

builder.add_edge(
    "claim_worker",
    "final_report"
)


# =============================================================
# 12. Final report -> END
# =============================================================

builder.add_edge(
    "final_report",
    END
)


# =============================================================
# 13. Compile
# =============================================================

graph = builder.compile()


# =============================================================
# 14. Input claims
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
# 15. Run workflow
# =============================================================

print("=" * 60)
print("NATIVE RETRY POLICY WORKFLOW")
print("=" * 60)

try:

    result = graph.invoke(
        {
            "claims": claims,
            "results": [],
            "report": "",
        }
    )

    print(
        "\nGraph completed successfully."
    )

except Exception as exc:

    print(
        "\nGraph execution failed."
    )

    print(
        f"Exception: {exc}"
    )


# =============================================================
# 16. Display results
# =============================================================

if "result" in locals():

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    for item in result["results"]:

        print(
            f"{item['claim_id']} | "
            f"{item['status']} | "
            f"Attempt {item['attempt']}"
        )


    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    print(
        result["report"]
    )


# =============================================================
# 17. Show attempts
# =============================================================

print("\n" + "=" * 60)
print("ATTEMPT SUMMARY")
print("=" * 60)

for claim_id, count in attempts.items():

    print(
        f"{claim_id} -> {count} attempt(s)"
    )


# =============================================================
# 18. Workflow summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    "Retry mechanism : LangGraph RetryPolicy"
)

print(
    "Maximum attempts: 2"
)

print(
    "Retry exception  : ValueError"
)

print(
    "Expected CLM003 : 2 attempts"
)