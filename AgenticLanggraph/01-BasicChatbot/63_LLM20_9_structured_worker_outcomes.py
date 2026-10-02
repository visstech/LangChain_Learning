
"""
============================================================
63_LLM20_9_structured_worker_outcomes.py
============================================================

LESSON:
LangGraph 20.9.11 - Structured Worker Outcomes

============================================================
WHAT THIS PROGRAM DOES
============================================================

This program demonstrates how to return a consistent,
structured result from every parallel LangGraph worker.

We continue the insurance claim-processing example from
Lesson 20.9.10.

Multiple claims are processed in parallel using Send().

Each worker returns the SAME result structure regardless of
whether the claim:

    - succeeds immediately
    - succeeds after retry
    - requires fallback
    - fails because of a system error

============================================================
KEY CONCEPTS
============================================================

1. Send()
   --------
   Dynamically sends each claim to the process_claim worker.

2. Parallel Processing
   --------------------
   Claims are processed independently.

3. RetryPolicy
   ------------
   A transient ConnectionError is automatically retried.

4. Error Classification
   ---------------------
   Errors are classified as:

       TRANSIENT
       BUSINESS
       SYSTEM

5. Recovery
   --------
   Errors result in:

       RETRY
       FALLBACK
       FAIL

6. TypedDict
   ----------
   ClaimResult defines the standard structure returned for
   every claim.

7. Structured Worker Outcome
   --------------------------
   Every worker returns the same fields:

       claim_id
       status
       attempts
       recovery
       error_type
       error

8. Reducer
   --------
   Annotated[list[ClaimResult], operator.add]

   Combines results produced by parallel workers.

============================================================
WHY STRUCTURED RESULTS MATTER
============================================================

Imagine processing 10,000 insurance claims.

If every worker returns a different structure, downstream
systems become difficult to maintain.

Instead, every worker should follow one contract:

    ClaimResult

This makes the result suitable for:

    - logging
    - auditing
    - monitoring
    - dashboards
    - testing
    - APIs
    - databases
    - downstream workflows

============================================================
EXPECTED FLOW
============================================================

                         START
                           |
                           v
                    Prepare Claims
                           |
                           v
                         Send()
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       CLM001           CLM002           CLM003
       SUCCESS          RETRY            FALLBACK
          |                |
          |             Attempt 2
          |                |
          |             SUCCESS
          |                |
          +----------------+----------------+
                           |
                       CLM004
                         FAIL
                           |
                           v
                         Fan-In
                           |
                           v
                  Structured Report
                           |
                           v
                          END

============================================================
IMPORTANT
============================================================

Parallel worker execution order is NOT guaranteed.

The final report is sorted by claim_id so that the output
is stable and easy to read.

============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy


# ============================================================
# CLAIM INPUT
# ============================================================

class Claim(TypedDict):
    """
    Represents one insurance claim to be processed.
    """

    claim_id: str
    type: str


# ============================================================
# STRUCTURED CLAIM RESULT
# ============================================================

class ClaimResult(TypedDict):
    """
    Standard result returned by every claim-processing worker.

    Every worker follows this same structure.

    claim_id:
        Unique insurance claim identifier.

    status:
        Final processing status.

    attempts:
        Number of processing attempts.

    recovery:
        Recovery strategy used.

    error_type:
        TRANSIENT, BUSINESS, SYSTEM, or None.

    error:
        Error message or None.
    """

    claim_id: str
    status: str
    attempts: int
    recovery: str
    error_type: str | None
    error: str | None


# ============================================================
# GRAPH STATE
# ============================================================

class ClaimState(TypedDict, total=False):
    """
    Shared LangGraph state.

    claims:
        List of claims created by prepare_claims.

    claim:
        Individual claim sent to a worker through Send().

    results:
        Structured results from all parallel workers.

    operator.add is used as the reducer so results from
    different workers are combined rather than overwritten.
    """

    claims: list[Claim]

    claim: Claim

    results: Annotated[list[ClaimResult], operator.add]


# ============================================================
# PREPARE CLAIMS
# ============================================================

def prepare_claims(state: ClaimState):
    """
    Create the claims that will be processed.
    """

    print("\nPreparing claims...")

    claims: list[Claim] = [
        {
            "claim_id": "CLM001",
            "type": "SUCCESS"
        },
        {
            "claim_id": "CLM002",
            "type": "TRANSIENT"
        },
        {
            "claim_id": "CLM003",
            "type": "BUSINESS"
        },
        {
            "claim_id": "CLM004",
            "type": "SYSTEM"
        }
    ]

    return {
        "claims": claims
    }


# ============================================================
# DISPATCH CLAIMS
# ============================================================

def dispatch_claims(state: ClaimState):
    """
    Create one Send() operation for every claim.

    Send(destination, payload)

    destination:
        The worker node that should process the claim.

    payload:
        State sent to that worker.
    """

    print("\nDispatching claims using Send...")

    return [
        Send(
            "process_claim",
            {
                "claim": claim
            }
        )
        for claim in state["claims"]
    ]


# ============================================================
# ERROR CLASSIFICATION
# ============================================================

def classify_error(error: Exception) -> str:
    """
    Convert Python exceptions into application-level
    error categories.
    """

    if isinstance(error, ConnectionError):
        return "TRANSIENT"

    if isinstance(error, ValueError):
        return "BUSINESS"

    return "SYSTEM"


# ============================================================
# RECOVERY DECISION
# ============================================================

def get_recovery_action(error_type: str) -> str:
    """
    Determine the recovery strategy based on error type.
    """

    if error_type == "TRANSIENT":
        return "RETRY"

    if error_type == "BUSINESS":
        return "FALLBACK"

    return "FAIL"


# ============================================================
# ATTEMPT TRACKING
# ============================================================

# Used only to simulate a transient failure.

attempts: dict[str, int] = {}


# ============================================================
# PROCESS CLAIM
# ============================================================

def process_claim(state: ClaimState):
    """
    Process one claim.

    Every successful execution returns a ClaimResult.

    A transient ConnectionError is intentionally raised so
    RetryPolicy can retry the worker.

    Business and system errors are converted into structured
    results so that they do not destroy the entire graph.
    """

    claim = state["claim"]

    claim_id = claim["claim_id"]

    claim_type = claim["type"]

    # --------------------------------------------------------
    # Track attempt number
    # --------------------------------------------------------

    attempts[claim_id] = attempts.get(claim_id, 0) + 1

    attempt = attempts[claim_id]

    print(
        f"Processing {claim_id} "
        f"(attempt {attempt})"
    )

    # ========================================================
    # SCENARIO 1 - SUCCESS
    # ========================================================

    if claim_type == "SUCCESS":

        print(
            f"{claim_id}: processed successfully."
        )

        result: ClaimResult = {
            "claim_id": claim_id,
            "status": "SUCCESS",
            "attempts": attempt,
            "recovery": "NONE",
            "error_type": None,
            "error": None
        }

        return {
            "results": [result]
        }

    # ========================================================
    # SCENARIO 2 - TRANSIENT ERROR
    # ========================================================

    if claim_type == "TRANSIENT":

        # Fail the first attempt.

        if attempt == 1:

            print(
                f"{claim_id}: "
                f"temporary connection failure."
            )

            raise ConnectionError(
                "Temporary connection failure"
            )

        # Second attempt succeeds.

        print(
            f"{claim_id}: "
            f"succeeded after retry."
        )

        result: ClaimResult = {
            "claim_id": claim_id,
            "status": "SUCCESS",
            "attempts": attempt,
            "recovery": "RETRY",
            "error_type": "TRANSIENT",
            "error": None
        }

        return {
            "results": [result]
        }

    # ========================================================
    # SCENARIO 3 - BUSINESS ERROR
    # ========================================================

    if claim_type == "BUSINESS":

        error = ValueError(
            "Claim not found"
        )

        error_type = classify_error(error)

        recovery = get_recovery_action(
            error_type
        )

        print(
            f"{claim_id}: "
            f"{error_type} error -> {recovery}"
        )

        result: ClaimResult = {
            "claim_id": claim_id,
            "status": "NOT_FOUND",
            "attempts": attempt,
            "recovery": recovery,
            "error_type": error_type,
            "error": str(error)
        }

        return {
            "results": [result]
        }

    # ========================================================
    # SCENARIO 4 - SYSTEM ERROR
    # ========================================================

    error = RuntimeError(
        "Unexpected internal processing failure"
    )

    error_type = classify_error(error)

    recovery = get_recovery_action(
        error_type
    )

    print(
        f"{claim_id}: "
        f"{error_type} error -> {recovery}"
    )

    result: ClaimResult = {
        "claim_id": claim_id,
        "status": "FAILED",
        "attempts": attempt,
        "recovery": recovery,
        "error_type": error_type,
        "error": str(error)
    }

    return {
        "results": [result]
    }


# ============================================================
# FINAL STRUCTURED REPORT
# ============================================================

def final_report(state: ClaimState):
    """
    Display the structured results produced by all workers.
    """

    print("\n" + "=" * 60)
    print("STRUCTURED FINAL REPORT")
    print("=" * 60)

    results = state.get("results", [])

    # --------------------------------------------------------
    # Sort by claim ID for stable output.
    # --------------------------------------------------------

    results = sorted(
        results,
        key=lambda result: result["claim_id"]
    )

    for result in results:

        print(
            f"\nClaim ID   : "
            f"{result['claim_id']}"
        )

        print(
            f"Status     : "
            f"{result['status']}"
        )

        print(
            f"Attempts   : "
            f"{result['attempts']}"
        )

        print(
            f"Recovery   : "
            f"{result['recovery']}"
        )

        print(
            f"Error Type : "
            f"{result['error_type']}"
        )

        print(
            f"Error      : "
            f"{result['error']}"
        )

    print("\n" + "=" * 60)
    print("GRAPH COMPLETED")
    print("=" * 60)


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(ClaimState)


# ============================================================
# ADD NODES
# ============================================================

builder.add_node(
    "prepare_claims",
    prepare_claims
)


# ------------------------------------------------------------
# process_claim has RetryPolicy.
#
# ConnectionError is retryable.
#
# max_attempts=2 means:
#
#     Attempt 1
#         |
#     ConnectionError
#         |
#     Attempt 2
#
# ------------------------------------------------------------

builder.add_node(
    "process_claim",
    process_claim,
    retry_policy=RetryPolicy(
        max_attempts=2,
        retry_on=ConnectionError
    )
)


builder.add_node(
    "final_report",
    final_report
)


# ============================================================
# GRAPH EDGES
# ============================================================

# START -> prepare_claims

builder.add_edge(
    START,
    "prepare_claims"
)


# prepare_claims -> dynamic Send()

builder.add_conditional_edges(
    "prepare_claims",
    dispatch_claims
)


# process_claim -> final_report

builder.add_edge(
    "process_claim",
    "final_report"
)


# final_report -> END

builder.add_edge(
    "final_report",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph = builder.compile()


# ============================================================
# RUN
# ============================================================

print("=" * 60)
print("20.9.11 - STRUCTURED WORKER OUTCOMES")
print("=" * 60)

# Reset simulation attempt tracking for a clean run.

attempts.clear()

graph.invoke({})

