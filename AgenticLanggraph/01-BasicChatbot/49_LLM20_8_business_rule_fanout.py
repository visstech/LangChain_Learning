"""
===============================================================
LangGraph 20.8.7 - Business-Rule-Based Dynamic Fan-Out
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates how business rules can control
dynamic fan-out.

Only claims that satisfy the business rule will be sent
to the worker using Send.

BUSINESS RULE
-------------
amount > RM 5000
    -> detailed analysis

amount <= RM 5000
    -> skip detailed analysis

LEARNING GOAL
-------------
Understand that Send can be created selectively.

The dispatcher does not have to send every input item
to the worker.

===============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


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

    # ---------------------------------------------------------
    # Reducer
    #
    # Multiple workers may return results at the same time.
    # operator.add combines all result lists.
    # ---------------------------------------------------------

    results: Annotated[
        list[dict],
        operator.add
    ]


# =============================================================
# 3. Dispatcher with business rule
# =============================================================

def dispatch_claims(state: OverallState):
    """
    Apply the business rule and create Send objects only
    for qualifying claims.

    BUSINESS RULE:

        amount > RM 5000
            -> send for detailed analysis

        amount <= RM 5000
            -> skip
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
        # Business rule
        # -----------------------------------------------------

        if amount > 5000:

            print(
                "Rule matched -> sending for detailed analysis"
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

        else:

            print(
                "Rule not matched -> skipping detailed analysis"
            )

    print(
        f"\nTotal worker tasks created: {len(sends)}"
    )

    return sends


# =============================================================
# 4. Detailed claim worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process a claim that passed the business rule.
    """

    claim_id = state["claim_id"]
    claim_type = state["claim_type"]
    amount = state["amount"]

    print(
        f"\nWorker processing {claim_id}"
    )

    print(
        f"Type   : {claim_type}"
    )

    print(
        f"Amount : RM {amount}"
    )

    result = {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "amount": amount,
        "analysis": "DETAILED_ANALYSIS_COMPLETED",
    }

    return {
        "results": [result]
    }


# =============================================================
# 5. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)


builder.add_node(
    "claim_worker",
    claim_worker
)


# =============================================================
# 6. Dynamic fan-out
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 7. Worker completion
# =============================================================

builder.add_edge(
    "claim_worker",
    END
)


# =============================================================
# 8. Compile graph
# =============================================================

graph = builder.compile()


# =============================================================
# 9. Input claims
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
# 10. Run workflow
# =============================================================

print("=" * 60)
print("BUSINESS-RULE-BASED FAN-OUT")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "results": [],
    }
)


# =============================================================
# 11. Display aggregated results
# =============================================================

print("\n" + "=" * 60)
print("AGGREGATED RESULTS")
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
        f"Analysis : {item['analysis']}"
    )


# =============================================================
# 12. Summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    f"Input claims          : {len(claims)}"
)

print(
    f"Worker tasks created  : {len(result['results'])}"
)

print(
    "Business rule         : amount > RM 5000"
)

print(
    "Fan-out               : SELECTIVE / DYNAMIC"
)

print(
    "Reducer               : operator.add"
)