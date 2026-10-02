"""
===============================================================
LangGraph 20.8.9 - Multi-level Dynamic Routing
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program routes insurance claims to different worker
nodes based on claim amount.

BUSINESS RULE
-------------
Amount <= RM 5000
    -> simple_worker

Amount > RM 5000 and <= RM 10000
    -> detailed_worker

Amount > RM 10000
    -> escalation_worker

The three worker nodes return structured results.

A reducer combines all results.

LEARNING GOAL
-------------
Understand:

    Dynamic routing
        +
    Send
        +
    Multiple worker nodes
        +
    Reducer

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
    # Reducer
    # ---------------------------------------------------------
    # Multiple workers can update "results".
    # operator.add combines the individual result lists.
    # ---------------------------------------------------------

    results: Annotated[
        list[dict],
        operator.add
    ]


# =============================================================
# 3. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    Apply business rules and dynamically route each claim.

    <= RM 5000
        -> simple_worker

    > RM 5000 and <= RM 10000
        -> detailed_worker

    > RM 10000
        -> escalation_worker
    """

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        claim_id = claim["claim_id"]
        claim_type = claim["claim_type"]
        amount = claim["amount"]

        print("\n" + "-" * 50)

        print(
            f"Checking {claim_id}"
        )

        print(
            f"Type   : {claim_type}"
        )

        print(
            f"Amount : RM {amount}"
        )

        # =====================================================
        # Path 1 - Simple processing
        # =====================================================

        if amount <= 5000:

            print(
                "Routing -> SIMPLE PROCESSING"
            )

            sends.append(
                Send(
                    "simple_worker",
                    {
                        "claim_id": claim_id,
                        "claim_type": claim_type,
                        "amount": amount,
                    }
                )
            )

        # =====================================================
        # Path 2 - Detailed analysis
        # =====================================================

        elif amount <= 10000:

            print(
                "Routing -> DETAILED ANALYSIS"
            )

            sends.append(
                Send(
                    "detailed_worker",
                    {
                        "claim_id": claim_id,
                        "claim_type": claim_type,
                        "amount": amount,
                    }
                )
            )

        # =====================================================
        # Path 3 - Escalation
        # =====================================================

        else:

            print(
                "Routing -> ESCALATION / SPECIAL REVIEW"
            )

            sends.append(
                Send(
                    "escalation_worker",
                    {
                        "claim_id": claim_id,
                        "claim_type": claim_type,
                        "amount": amount,
                    }
                )
            )

    print("\n" + "=" * 50)

    print(
        f"Total dynamic branches created: {len(sends)}"
    )

    return sends


# =============================================================
# 4. Simple worker
# =============================================================

def simple_worker(state: ClaimWorkerState):
    """
    Process a low-value claim using a simple workflow.
    """

    print(
        f"\nSimple worker processing "
        f"{state['claim_id']}"
    )

    result = {
        "claim_id": state["claim_id"],
        "claim_type": state["claim_type"],
        "amount": state["amount"],
        "route": "SIMPLE",
        "status": "PROCESSED",
        "reason": "Low-value claim",
    }

    return {
        "results": [result]
    }


# =============================================================
# 5. Detailed worker
# =============================================================

def detailed_worker(state: ClaimWorkerState):
    """
    Process a medium-value claim using detailed analysis.
    """

    print(
        f"\nDetailed worker processing "
        f"{state['claim_id']}"
    )

    result = {
        "claim_id": state["claim_id"],
        "claim_type": state["claim_type"],
        "amount": state["amount"],
        "route": "DETAILED",
        "status": "ANALYZED",
        "reason": "Medium-value claim",
    }

    return {
        "results": [result]
    }


# =============================================================
# 6. Escalation worker
# =============================================================

def escalation_worker(state: ClaimWorkerState):
    """
    Process a high-value claim using an escalation workflow.
    """

    print(
        f"\nEscalation worker processing "
        f"{state['claim_id']}"
    )

    result = {
        "claim_id": state["claim_id"],
        "claim_type": state["claim_type"],
        "amount": state["amount"],
        "route": "ESCALATION",
        "status": "ESCALATED",
        "reason": "High-value claim requires special review",
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


# Add all worker nodes.
builder.add_node(
    "simple_worker",
    simple_worker
)

builder.add_node(
    "detailed_worker",
    detailed_worker
)

builder.add_node(
    "escalation_worker",
    escalation_worker
)


# =============================================================
# 8. Dynamic fan-out
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 9. All worker paths end the workflow branch
# =============================================================

builder.add_edge(
    "simple_worker",
    END
)

builder.add_edge(
    "detailed_worker",
    END
)

builder.add_edge(
    "escalation_worker",
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
        "amount": 8000,
    },

    {
        "claim_id": "CLM003",
        "claim_type": "Travel",
        "amount": 15000,
    },

    {
        "claim_id": "CLM004",
        "claim_type": "Motor",
        "amount": 5000,
    },

    {
        "claim_id": "CLM005",
        "claim_type": "Health",
        "amount": 10000,
    },

    {
        "claim_id": "CLM006",
        "claim_type": "Travel",
        "amount": 20000,
    },
]


# =============================================================
# 12. Run workflow
# =============================================================

print("=" * 60)
print("MULTI-LEVEL DYNAMIC ROUTING")
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
print("FINAL AGGREGATED RESULTS")
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
        f"Route    : {item['route']}"
    )

    print(
        f"Status   : {item['status']}"
    )

    print(
        f"Reason   : {item['reason']}"
    )


# =============================================================
# 14. Final summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    f"Input claims       : {len(claims)}"
)

print(
    f"Final results      : {len(result['results'])}"
)

print(
    "Route 1            : <= RM 5000 -> SIMPLE"
)

print(
    "Route 2            : RM 5001-10000 -> DETAILED"
)

print(
    "Route 3            : > RM 10000 -> ESCALATION"
)

print(
    "Reducer            : operator.add"
)