
"""
============================================================
62_LLM20_9_resilient_parallel_processing.py
============================================================

LESSON:
LangGraph 20.9.10 - Resilient Parallel Processing

============================================================
WHAT THIS PROGRAM DOES
============================================================

This program demonstrates how to build a resilient parallel
claim-processing workflow using LangGraph.

Multiple insurance claims are processed in parallel using
LangGraph's Send() API.

Each claim is processed independently.

If one claim has a problem, the other claims should continue
processing.

The workflow demonstrates:

    TRANSIENT ERROR -> RETRY
    BUSINESS ERROR  -> FALLBACK
    SYSTEM ERROR    -> FAIL

The important production concept is:

    FAILURE ISOLATION

One failed worker should not automatically destroy the
results produced by other workers.

============================================================
KEY CONCEPTS
============================================================

1. Send()
   --------
   Dynamically sends individual claims to the worker node.

2. Parallel Processing
   --------------------
   Multiple claims can be processed independently.

3. Retry
   -----
   Temporary errors can be retried.

4. Error Classification
   ---------------------
   Errors are classified as:

       TRANSIENT
       BUSINESS
       SYSTEM

5. Recovery
   --------
   Based on the error type:

       RETRY
       FALLBACK
       FAIL

6. Reducer
   --------
   Annotated[list, operator.add]

   Multiple worker results are combined into one list.

7. Failure Isolation
   ------------------
   A failure in one claim should not remove the successful
   results of other claims.

============================================================
EXPECTED FLOW
============================================================

                        START
                          |
                          v
                  prepare_claims
                          |
                          v
                    Send() Fan-Out
                          |
             +------------+------------+
             |            |            |
             v            v            v
          CLM001       CLM002       CLM003
          SUCCESS      RETRY       FALLBACK
             |            |            |
             |            v            |
             |         SUCCESS         |
             |                         |
             +------------+------------+
                          |
                     CLM004
                       FAIL
                          |
                          v
                       Fan-In
                          |
                          v
                    final_report
                          |
                          v
                         END

============================================================
IMPORTANT
============================================================

The exact execution order of parallel workers is NOT
guaranteed.

For example:

    CLM001
    CLM003
    CLM004
    CLM002

may appear in a different order during different runs.

That is normal for parallel execution.

============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy


# ============================================================
# STATE DEFINITION
# ============================================================

class ClaimState(TypedDict, total=False):
    """
    Shared state used by the LangGraph workflow.

    claims:
        List of claims prepared for processing.

    claim:
        Individual claim received by a worker.

    results:
        Results returned by parallel workers.

        Annotated[list, operator.add] tells LangGraph to
        combine results from multiple workers instead of
        replacing the existing list.
    """

    claims: list[dict]

    claim: dict

    results: Annotated[list, operator.add]


# ============================================================
# PREPARE CLAIMS
# ============================================================

def prepare_claims(state: ClaimState):
    """
    Prepare the claims that will be processed.

    Each claim has a type that determines its behavior.
    """

    print("\nPreparing claims...")

    claims = [
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
# DISPATCH CLAIMS USING SEND
# ============================================================

def dispatch_claims(state: ClaimState):
    """
    Dynamically create one Send() operation per claim.

    Send(destination, payload)

    First argument:
        Name of the destination worker node.

    Second argument:
        State/payload sent to that worker.
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

def classify_error(error):
    """
    Convert Python exceptions into business-level categories.

    ConnectionError:
        Temporary infrastructure problem.

    ValueError:
        Business/data validation problem.

    Everything else:
        Unexpected system problem.
    """

    if isinstance(error, ConnectionError):
        return "TRANSIENT"

    if isinstance(error, ValueError):
        return "BUSINESS"

    return "SYSTEM"


# ============================================================
# RECOVERY DECISION
# ============================================================

def get_recovery_action(error_type):
    """
    Determine the appropriate recovery strategy.
    """

    if error_type == "TRANSIENT":
        return "RETRY"

    if error_type == "BUSINESS":
        return "FALLBACK"

    return "FAIL"


# ============================================================
# ATTEMPT TRACKING
# ============================================================

# This dictionary is used only for this learning example
# to simulate a transient error on the first attempt.

attempts = {}


# ============================================================
# PROCESS CLAIM
# ============================================================

def process_claim(state: ClaimState):
    """
    Process one individual claim.

    Each Send() invocation receives one claim.

    The function demonstrates four scenarios:

        SUCCESS
        TRANSIENT -> RETRY -> SUCCESS
        BUSINESS  -> FALLBACK
        SYSTEM    -> FAIL
    """

    claim = state["claim"]

    claim_id = claim["claim_id"]

    claim_type = claim["type"]

    # --------------------------------------------------------
    # Track attempts for this claim
    # --------------------------------------------------------

    attempts[claim_id] = attempts.get(claim_id, 0) + 1

    attempt = attempts[claim_id]

    print(
        f"Processing {claim_id} "
        f"(attempt {attempt})"
    )

    # ========================================================
    # SCENARIO 1
    # SUCCESS
    # ========================================================

    if claim_type == "SUCCESS":

        print(
            f"{claim_id}: processed successfully."
        )

        return {
            "results": [
                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": attempt,
                    "recovery": "NONE"
                }
            ]
        }

    # ========================================================
    # SCENARIO 2
    # TRANSIENT ERROR
    # ========================================================

    if claim_type == "TRANSIENT":

        # Simulate temporary failure on first attempt.

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

        return {
            "results": [
                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": attempt,
                    "recovery": "RETRY"
                }
            ]
        }

    # ========================================================
    # SCENARIO 3
    # BUSINESS ERROR
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

        # FALLBACK:
        # Instead of crashing the workflow, return a
        # controlled NOT_FOUND result.

        return {
            "results": [
                {
                    "claim_id": claim_id,
                    "status": "NOT_FOUND",
                    "attempts": attempt,
                    "recovery": recovery,
                    "error_type": error_type,
                    "error": str(error)
                }
            ]
        }

    # ========================================================
    # SCENARIO 4
    # SYSTEM ERROR
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

    # FAIL:
    # Return a controlled failure result rather than allowing
    # one worker failure to destroy the complete report.

    return {
        "results": [
            {
                "claim_id": claim_id,
                "status": "FAILED",
                "attempts": attempt,
                "recovery": recovery,
                "error_type": error_type,
                "error": str(error)
            }
        ]
    }


# ============================================================
# FINAL REPORT
# ============================================================

def final_report(state: ClaimState):
    """
    Display all results collected from the parallel workers.

    The reducer combines individual worker results into
    state["results"].
    """

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    results = state.get("results", [])

    # Sort only for a stable report.
    #
    # Parallel execution order is not guaranteed, so sorting
    # makes the final report easier to read.

    results = sorted(
        results,
        key=lambda result: result["claim_id"]
    )

    for result in results:

        print(
            f"\n{result['claim_id']} -> "
            f"{result['status']}"
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


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(ClaimState)


# ------------------------------------------------------------
# Add nodes
# ------------------------------------------------------------

builder.add_node(
    "prepare_claims",
    prepare_claims
)

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


# ------------------------------------------------------------
# START -> prepare_claims
# ------------------------------------------------------------

builder.add_edge(
    START,
    "prepare_claims"
)


# ------------------------------------------------------------
# prepare_claims -> dynamic Send()
#
# dispatch_claims() is a routing function.
#
# IMPORTANT:
# It is NOT added as a normal node.
#
# It returns Send() objects that dynamically route each
# claim to process_claim.
# ------------------------------------------------------------

builder.add_conditional_edges(
    "prepare_claims",
    dispatch_claims
)


# ------------------------------------------------------------
# process_claim -> final_report
# ------------------------------------------------------------

builder.add_edge(
    "process_claim",
    "final_report"
)


# ------------------------------------------------------------
# final_report -> END
# ------------------------------------------------------------

builder.add_edge(
    "final_report",
    END
)


# ============================================================
# COMPILE GRAPH
# ============================================================

graph = builder.compile()


# ============================================================
# RUN GRAPH
# ============================================================

print("=" * 60)
print("20.9.10 - RESILIENT PARALLEL PROCESSING")
print("=" * 60)

graph.invoke({})
