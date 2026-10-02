"""
===============================================================
LangGraph 20.8.8 - Handle Both Paths in Dynamic Fan-Out
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates business-rule-based dynamic
routing where BOTH paths produce a result.

BUSINESS RULE
-------------
amount > RM 5000
    -> detailed analysis worker

amount <= RM 5000
    -> skipped
    -> no detailed analysis required

IMPORTANT
---------
Every claim must appear in the final result.

Therefore:

    Qualifying claim
        -> claim_worker
        -> detailed result

    Non-qualifying claim
        -> skip_worker
        -> SKIPPED result

Both results are aggregated using a reducer.

LEARNING GOAL
-------------
Understand:

    Dynamic routing
        +
    Multiple target nodes
        +
    Reducer
        +
    Complete result coverage

===============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# =============================================================
# 1. Worker state for detailed analysis
# =============================================================

class ClaimWorkerState(TypedDict):
    claim_id: str
    claim_type: str
    amount: float


# =============================================================
# 2. Worker state for skipped claims
# =============================================================

class SkipWorkerState(TypedDict):
    claim_id: str
    claim_type: str
    amount: float


# =============================================================
# 3. Overall graph state
# =============================================================

class OverallState(TypedDict):

    claims: list[dict]

    # ---------------------------------------------------------
    # Reducer
    #
    # Multiple branches update "results".
    #
    # operator.add combines all result lists.
    # ---------------------------------------------------------

    results: Annotated[
        list[dict],
        operator.add
    ]


# =============================================================
# 4. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    Dynamically route EVERY claim.

    Rule:

        amount > RM 5000
            -> claim_worker

        amount <= RM 5000
            -> skip_worker

    Both paths create a result.
    """

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        claim_id = claim["claim_id"]
        amount = claim["amount"]

        print(
            f"\nChecking {claim_id}"
        )

        print(
            f"Amount: RM {amount}"
        )

        # -----------------------------------------------------
        # Path 1 - Detailed analysis
        # -----------------------------------------------------

        if amount > 5000:

            print(
                "Rule matched -> detailed analysis"
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

        # -----------------------------------------------------
        # Path 2 - Skip detailed analysis
        # -----------------------------------------------------

        else:

            print(
                "Rule not matched -> skipping analysis"
            )

            sends.append(
                Send(
                    "skip_worker",
                    {
                        "claim_id": claim["claim_id"],
                        "claim_type": claim["claim_type"],
                        "amount": claim["amount"],
                    }
                )
            )

    print(
        f"\nTotal branches created: {len(sends)}"
    )

    return sends


# =============================================================
# 5. Detailed analysis worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Perform detailed analysis for qualifying claims.
    """

    claim_id = state["claim_id"]
    claim_type = state["claim_type"]
    amount = state["amount"]

    print(
        f"\nDetailed worker processing {claim_id}"
    )

    result = {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "amount": amount,
        "status": "ANALYZED",
        "reason": "Claim qualified for detailed analysis",
    }

    return {
        "results": [result]
    }


# =============================================================
# 6. Skip worker
# =============================================================

def skip_worker(state: SkipWorkerState):
    """
    Create a result for claims that do not require
    detailed analysis.
    """

    claim_id = state["claim_id"]
    claim_type = state["claim_type"]
    amount = state["amount"]

    print(
        f"\nSkip worker processing {claim_id}"
    )

    result = {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "amount": amount,
        "status": "SKIPPED",
        "reason": "Claim amount does not require detailed analysis",
    }

    return {
        "results": [result]
    }


# =============================================================
# 7. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)


# Add both possible worker nodes.
builder.add_node(
    "claim_worker",
    claim_worker
)

builder.add_node(
    "skip_worker",
    skip_worker
)


# =============================================================
# 8. Dynamic fan-out
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 9. Both paths finish the workflow
# =============================================================

builder.add_edge(
    "claim_worker",
    END
)

builder.add_edge(
    "skip_worker",
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
        "amount": 3000,
    },

    {
        "claim_id": "CLM002",
        "claim_type": "Health",
        "amount": 12000,
    },

    {
        "claim_id": "CLM003",
        "claim_type": "Travel",
        "amount": 4500,
    },

    {
        "claim_id": "CLM004",
        "claim_type": "Motor",
        "amount": 9000,
    },
]


# =============================================================
# 12. Run workflow
# =============================================================

print("=" * 60)
print("BOTH-PATH DYNAMIC FAN-OUT")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "results": [],
    }
)


# =============================================================
# 13. Display final results
# =============================================================

print("\n" + "=" * 60)
print("FINAL RESULTS - ALL CLAIMS")
print("=" * 60)

for item in result["results"]:

    print(
        f"\nClaim ID : {item['claim_id']}"
    )

    print(
        f"Type     : {item['claim_type']}"
    )

    print(
        f"Amount   : RM {item['amount']}"
    )

    print(
        f"Status   : {item['status']}"
    )

    print(
        f"Reason   : {item['reason']}"
    )


# =============================================================
# 14. Summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    f"Input claims      : {len(claims)}"
)

print(
    f"Final results     : {len(result['results'])}"
)

print(
    "Business rule     : amount > RM 5000"
)

print(
    "Detailed path     : claim_worker"
)

print(
    "Skip path         : skip_worker"
)

print(
    "Reducer           : operator.add"
)