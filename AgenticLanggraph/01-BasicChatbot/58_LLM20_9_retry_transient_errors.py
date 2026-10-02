"""
===============================================================
LangGraph 20.9.6 - Retry Only Transient Errors
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates selective retry behavior.

We have two different types of failures:

    CLM003
        -> ConnectionError
        -> treated as TRANSIENT
        -> retry
        -> succeeds on second attempt

    CLM004
        -> ValueError
        -> treated as PERMANENT
        -> DO NOT RETRY
        -> graph execution fails

LEARNING GOAL
-------------
Understand that production systems should NOT retry every
exception.

Retry transient failures such as:

    - temporary network failure
    - connection timeout
    - temporary service unavailability

Do not automatically retry permanent failures such as:

    - invalid input
    - invalid business rule
    - programming errors
    - invalid identifiers

RETRY RULE
----------
Only ConnectionError should be retried.

We implement:

    retry_on = should_retry

where should_retry() returns:

    True  -> retry
    False -> do not retry

IMPORTANT
---------
The worker must allow the exception to escape.

DO NOT catch the exception inside the worker before
RetryPolicy sees it.

FLOW
----
CLM003
    ConnectionError
        ↓
    RetryPolicy
        ↓
    Attempt 2
        ↓
    SUCCESS

CLM004
    ValueError
        ↓
    RetryPolicy checks exception
        ↓
    ValueError is not retryable
        ↓
    Graph fails

===============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy


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
# 3. Track attempts
# =============================================================

attempts: dict[str, int] = {}


# =============================================================
# 4. Retry decision function
# =============================================================

def should_retry(exc: Exception) -> bool:
    """
    Decide whether LangGraph should retry the exception.

    ConnectionError
        -> retry

    Everything else
        -> do not retry
    """

    print(
        f"\nRetry policy checking: "
        f"{type(exc).__name__}"
    )

    if isinstance(exc, ConnectionError):

        print(
            "-> TRANSIENT ERROR: retry allowed"
        )

        return True

    print(
        "-> NON-RETRYABLE ERROR: retry not allowed"
    )

    return False


# =============================================================
# 5. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    Create one worker branch for every claim.
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
# 6. Claim worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process one claim.

    CLM003:
        ConnectionError on first attempt.
        Succeeds on second attempt.

    CLM004:
        ValueError.
        This is NOT retryable.
    """

    claim_id = state["claim_id"]

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


    # =========================================================
    # CLM003 - transient failure
    # =========================================================

    if (
        claim_id == "CLM003"
        and current_attempt == 1
    ):

        print(
            "❌ CLM003: temporary connection problem"
        )

        raise ConnectionError(
            "Temporary connection failure"
        )


    # =========================================================
    # CLM004 - permanent failure
    # =========================================================

    if claim_id == "CLM004":

        print(
            "❌ CLM004: invalid business data"
        )

        raise ValueError(
            "Invalid claim data"
        )


    # =========================================================
    # Successful processing
    # =========================================================

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
# 7. Final report
# =============================================================

def final_report(state: OverallState):

    print(
        "\n>>> FINAL REPORT NODE STARTED <<<"
    )

    return {
        "report": (
            f"Processed "
            f"{len(state['results'])} claims."
        )
    }


# =============================================================
# 8. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)


# =============================================================
# 9. Add claim worker with selective RetryPolicy
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
        retry_on=should_retry,
    ),
)


# =============================================================
# 10. Final report node
# =============================================================

builder.add_node(
    "final_report",
    final_report
)


# =============================================================
# 11. Fan-out
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 12. Workers -> Final Report
# =============================================================

builder.add_edge(
    "claim_worker",
    "final_report"
)


# =============================================================
# 13. Final Report -> END
# =============================================================

builder.add_edge(
    "final_report",
    END
)


# =============================================================
# 14. Compile
# =============================================================

graph = builder.compile()


# =============================================================
# 15. Input claims
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
# 16. Execute workflow
# =============================================================

print("=" * 60)
print("SELECTIVE RETRY POLICY WORKFLOW")
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

    print("\n" + "=" * 60)
    print("GRAPH EXECUTION FAILED")
    print("=" * 60)

    print(
        f"Exception type: {type(exc).__name__}"
    )

    print(
        f"Exception     : {exc}"
    )


# =============================================================
# 17. Attempt summary
# =============================================================

print("\n" + "=" * 60)
print("ATTEMPT SUMMARY")
print("=" * 60)

for claim_id, count in attempts.items():

    print(
        f"{claim_id} -> "
        f"{count} attempt(s)"
    )


# =============================================================
# 18. Workflow summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    "Retryable error : ConnectionError"
)

print(
    "Non-retryable   : ValueError"
)

print(
    "Maximum attempts: 2"
)

print(
    "Goal            : retry only transient failures"
)