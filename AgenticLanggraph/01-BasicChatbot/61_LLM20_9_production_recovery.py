"""
============================================================
20.9.9 - PRODUCTION RETRY + RECOVERY PATTERN
============================================================

WHAT THIS PROGRAM DOES
----------------------
This program demonstrates how a LangGraph workflow can use
different recovery strategies depending on the type of error.

We process multiple insurance claims using Send().

Each claim can produce:

1. SUCCESS
2. TRANSIENT error  -> RETRY
3. BUSINESS error   -> FALLBACK
4. SYSTEM error     -> FAIL

KEY CONCEPTS
------------
1. Send()
   Dynamically sends individual claims to process_claim().

2. Annotated[list, operator.add]
   Combines results produced by multiple parallel workers.

3. RetryPolicy
   Automatically retries retryable exceptions.

4. Error Classification
   Determines whether an error is TRANSIENT, BUSINESS,
   or SYSTEM.

5. Recovery Strategy
   Determines whether to RETRY, FALLBACK, or FAIL.

IMPORTANT
---------
Retryable exceptions must escape the processing node so
LangGraph's RetryPolicy can detect them.

EXPECTED FLOW
-------------
CLM001 -> SUCCESS
CLM002 -> TRANSIENT -> RETRY -> SUCCESS
CLM003 -> BUSINESS -> FALLBACK -> NOT_FOUND
CLM004 -> SYSTEM -> FAIL
============================================================
"""

import operator

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy


# ============================================================
# 1. STATE DEFINITION
# ============================================================

class State(TypedDict, total=False):
    """
    Shared state used by the LangGraph workflow.
    """

    claims: list

    # Multiple parallel workers can update this field.
    # operator.add combines their lists.
    results: Annotated[
        list,
        operator.add
    ]


# ============================================================
# 2. CLAIM DATA
# ============================================================

claims_data = [
    {
        "claim_id": "CLM001",
        "behavior": "success"
    },
    {
        "claim_id": "CLM002",
        "behavior": "transient"
    },
    {
        "claim_id": "CLM003",
        "behavior": "business"
    },
    {
        "claim_id": "CLM004",
        "behavior": "system"
    },
]


# ============================================================
# 3. ATTEMPT TRACKING
# ============================================================

attempts = {}


# ============================================================
# 4. ERROR CLASSIFICATION
# ============================================================

def classify_error(error):
    """
    Classifies an exception into a business category.

    ConnectionError -> TRANSIENT
    ValueError      -> BUSINESS
    Other errors    -> SYSTEM
    """

    if isinstance(error, ConnectionError):
        return "TRANSIENT"

    if isinstance(error, ValueError):
        return "BUSINESS"

    return "SYSTEM"


# ============================================================
# 5. RECOVERY STRATEGY
# ============================================================

def get_recovery_action(error_type):
    """
    Determines what action should be taken for each
    error classification.
    """

    if error_type == "TRANSIENT":
        return "RETRY"

    if error_type == "BUSINESS":
        return "FALLBACK"

    return "FAIL"


# ============================================================
# 6. DISPATCH CLAIMS
# ============================================================

def dispatch_claims(state: State):

    print("\nDispatching claims using Send...\n")

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
# 7. PROCESS CLAIM
# ============================================================

def process_claim(state: State):

    claim_id = state["claim_id"]
    behavior = state["behavior"]

    # Track attempts
    attempts[claim_id] = attempts.get(claim_id, 0) + 1

    current_attempt = attempts[claim_id]

    print(
        f"Processing {claim_id} "
        f"(attempt {current_attempt})"
    )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if behavior == "success":

        print(f"{claim_id}: processed successfully.")

        return {
            "results": [
                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": current_attempt,
                    "recovery": "NONE",
                }
            ]
        }

    # --------------------------------------------------------
    # TRANSIENT ERROR
    # --------------------------------------------------------

    if behavior == "transient":

        if current_attempt == 1:

            print(
                f"{claim_id}: temporary connection failure."
            )

            # IMPORTANT:
            # Let this exception escape so RetryPolicy
            # can detect it and retry the node.
            raise ConnectionError(
                "Temporary database connection failure"
            )

        print(
            f"{claim_id}: succeeded after retry."
        )

        return {
            "results": [
                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": current_attempt,
                    "recovery": "RETRY",
                }
            ]
        }

    # --------------------------------------------------------
    # BUSINESS ERROR
    # --------------------------------------------------------

    if behavior == "business":

        try:

            raise ValueError(
                "Claim not found"
            )

        except ValueError as error:

            error_type = classify_error(error)

            recovery = get_recovery_action(
                error_type
            )

            print(
                f"{claim_id}: "
                f"{error_type} error -> {recovery}"
            )

            # FALLBACK means we don't retry.
            # Instead we return a safe alternative result.
            return {
                "results": [
                    {
                        "claim_id": claim_id,
                        "status": "NOT_FOUND",
                        "attempts": current_attempt,
                        "error_type": error_type,
                        "error": str(error),
                        "recovery": recovery,
                    }
                ]
            }

    # --------------------------------------------------------
    # SYSTEM ERROR
    # --------------------------------------------------------

    if behavior == "system":

        try:

            raise RuntimeError(
                "Unexpected internal processing failure"
            )

        except RuntimeError as error:

            error_type = classify_error(error)

            recovery = get_recovery_action(
                error_type
            )

            print(
                f"{claim_id}: "
                f"{error_type} error -> {recovery}"
            )

            return {
                "results": [
                    {
                        "claim_id": claim_id,
                        "status": "FAILED",
                        "attempts": current_attempt,
                        "error_type": error_type,
                        "error": str(error),
                        "recovery": recovery,
                    }
                ]
            }


# ============================================================
# 8. RETRY DECISION
# ============================================================

def should_retry(error):
    """
    Only ConnectionError is retryable.

    Other errors should not be retried automatically.
    """

    return isinstance(
        error,
        ConnectionError
    )


# ============================================================
# 9. BUILD GRAPH
# ============================================================

builder = StateGraph(State)


builder.add_node(
    "process_claim",
    process_claim,
    retry_policy=RetryPolicy(
        max_attempts=3,
        retry_on=should_retry
    )
)

# START directly uses dispatch_claims as a
# conditional routing function.
#
# dispatch_claims() returns a list of Send() objects.
builder.add_conditional_edges(
    START,
    dispatch_claims
)

builder.add_edge(
    "process_claim",
    END
)


# ============================================================
# 11. COMPILE
# ============================================================

graph = builder.compile()


# ============================================================
# 12. RUN GRAPH
# ============================================================

print("=" * 60)
print("20.9.9 - PRODUCTION RETRY + RECOVERY")
print("=" * 60)

print("\nPreparing claims...")

final_state = graph.invoke(
    {
        "claims": claims_data,
        "results": [],
    }
)


# ============================================================
# 13. FINAL REPORT
# ============================================================

print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)

for result in final_state["results"]:

    print(
        f"\n{result['claim_id']} "
        f"-> {result['status']}"
    )

    print(
        f"   Attempts : "
        f"{result['attempts']}"
    )

    print(
        f"   Recovery : "
        f"{result['recovery']}"
    )

    if "error_type" in result:

        print(
            f"   Error Type : "
            f"{result['error_type']}"
        )

        print(
            f"   Error      : "
            f"{result['error']}"
        )


print("\n" + "=" * 60)
print("GRAPH COMPLETED")
print("=" * 60)