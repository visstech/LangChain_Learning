"""
============================================================
20.9.7 - Retry + Graceful Failure
============================================================

PURPOSE
-------
This program demonstrates how to combine:

1. Send
2. RetryPolicy
3. Node-level error handling
4. Structured failure results
5. Reducer / fan-in

The goal is to build a resilient LangGraph workflow where:

- Temporary errors are retried automatically.
- Permanent errors do not crash the entire graph.
- Failed items are converted into structured results.
- Other parallel workers can continue processing.

EXPECTED FLOW
-------------
START
  |
  v
Create Claims
  |
  v
Send -> Parallel Claim Workers
  |
  +--> CLM001
  |
  +--> CLM002
  |
  +--> CLM003
  |
  +--> CLM004
  |
  v
RetryPolicy
  |
  v
Graceful Failure Handler
  |
  v
Reducer / Fan-in
  |
  v
Final Report
  |
  v
END

KEY CONCEPTS
------------
- Send
- RetryPolicy
- Transient failure
- Permanent failure
- Graceful failure
- Structured error result
- Reducer
- Fan-out / Fan-in

IMPORTANT
---------
RetryPolicy handles retryable exceptions.

The error handler handles an exception after the retry
mechanism has exhausted its attempts.

This means the two mechanisms have different responsibilities.
============================================================
"""

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy
import operator


# ============================================================
# 1. GRAPH STATE
# ============================================================

class State(TypedDict):
    claims: list
    results: Annotated[list, operator.add]


# ============================================================
# 2. WORKER STATE
# ============================================================

class ClaimWorkerState(TypedDict):
    claim_id: str
    results: Annotated[list, operator.add]


# ============================================================
# 3. CLAIM DATA
# ============================================================

claims_data = [
    {
        "claim_id": "CLM001",
        "behavior": "success"
    },
    {
        "claim_id": "CLM002",
        "behavior": "success"
    },
    {
        "claim_id": "CLM003",
        "behavior": "transient"
    },
    {
        "claim_id": "CLM004",
        "behavior": "permanent"
    },
]


# ============================================================
# 4. PREPARE CLAIMS
# ============================================================

def prepare_claims(state: State):

    print("\nPreparing claims...")

    return {
        "claims": claims_data
    }


# ============================================================
# 5. FAN-OUT USING SEND
# ============================================================

def dispatch_claims(state: State):

    print("\nDispatching claims using Send...")

    return [
        Send(
            "process_claim",
            {
                "claim_id": claim["claim_id"],
                "behavior": claim["behavior"],
            }
        )
        for claim in state["claims"]
    ]


# ============================================================
# 6. WORKER NODE
# ============================================================

attempts = {}


def process_claim(state):

    claim_id = state["claim_id"]

    attempts[claim_id] = attempts.get(claim_id, 0) + 1

    attempt = attempts[claim_id]

    print(
        f"\nProcessing {claim_id} "
        f"(attempt {attempt})"
    )

    # ========================================================
    # SUCCESSFUL CLAIMS
    # ========================================================

    if claim_id in ["CLM001", "CLM002"]:

        print(
            f"{claim_id} processed successfully."
        )

        return {
            "results": [
                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": attempt
                }
            ]
        }

    # ========================================================
    # TRANSIENT FAILURE
    #
    # IMPORTANT:
    # We intentionally DO NOT catch ConnectionError.
    #
    # This allows RetryPolicy to handle it.
    # ========================================================

    if claim_id == "CLM003":

        if attempt == 1:

            print(
                f"{claim_id}: transient error occurred."
            )

            raise ConnectionError(
                "Temporary service connection failure"
            )

        print(
            f"{claim_id} succeeded after retry."
        )

        return {
            "results": [
                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": attempt
                }
            ]
        }

    # ========================================================
    # PERMANENT FAILURE
    #
    # Catch this locally and convert it into a structured
    # failure result.
    # ========================================================

    if claim_id == "CLM004":

        try:

            print(
                f"{claim_id}: permanent error occurred."
            )

            raise ValueError(
                "Permanent claim processing failure"
            )

        except ValueError as error:

            print(
                f"{claim_id}: gracefully handled."
            )

            return {
                "results": [
                    {
                        "claim_id": claim_id,
                        "status": "FAILED",
                        "attempts": attempt,
                        "error": str(error)
                    }
                ]
            }

# ============================================================
# 7. RETRY DECISION
# ============================================================

def should_retry(error: Exception) -> bool:

    return isinstance(error, ConnectionError)


# ============================================================
# 8. ERROR HANDLER
# ============================================================

def handle_claim_failure(
    state: ClaimWorkerState,
    error: Exception
):

    claim_id = state["claim_id"]

    print(
        f"\nGracefully handling failure for {claim_id}"
    )

    print(
        f"Error: {error}"
    )

    return {
        "results": [
            {
                "claim_id": claim_id,
                "status": "FAILED",
                "error": str(error)
            }
        ]
    }


# ============================================================
# 9. BUILD GRAPH
# ============================================================

builder = StateGraph(State)


builder.add_node(
    "prepare_claims",
    prepare_claims
)


builder.add_node(
    "process_claim",
    process_claim,
    retry_policy=RetryPolicy(
        max_attempts=3,
        retry_on=should_retry,
    ),
    error_handler=handle_claim_failure,
)


builder.add_edge(
    START,
    "prepare_claims"
)


builder.add_conditional_edges(
    "prepare_claims",
    dispatch_claims,
)


builder.add_edge(
    "process_claim",
    END
)


# ============================================================
# 10. COMPILE
# ============================================================

graph = builder.compile()


# ============================================================
# 11. RUN
# ============================================================

print("\n" + "=" * 60)
print("20.9.7 - RETRY + GRACEFUL FAILURE")
print("=" * 60)


initial_state = {
    "claims": [],
    "results": []
}


final_state = graph.invoke(initial_state)


# ============================================================
# 12. FINAL REPORT
# ============================================================

print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)


for result in final_state["results"]:

    print(
        f"{result['claim_id']} -> "
        f"{result['status']}"
    )

    if "attempts" in result:

        print(
            f"   Attempts : {result['attempts']}"
        )

    if "error" in result:

        print(
            f"   Error    : {result['error']}"
        )


print("\n" + "=" * 60)
print("GRAPH COMPLETED")
print("=" * 60)