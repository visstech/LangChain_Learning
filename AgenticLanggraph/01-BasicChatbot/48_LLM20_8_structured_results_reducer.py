"""
===============================================================
LangGraph 20.8.6 - Structured Results + Reducer
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates:

    Dynamic Fan-out
          +
    Worker-specific processing
          +
    Structured worker results
          +
    Reducer-based Fan-in

Each claim worker evaluates one claim.

RULE:
-----
Amount <= RM 5000
    -> APPROVED

Amount > RM 5000 and <= RM 10000
    -> REVIEW

Amount > RM 10000
    -> REJECTED

Each worker returns a structured result.

The reducer combines all worker results into one list.

LEARNING GOAL
-------------
Understand:

    1 -> Many -> 1

and how a reducer combines parallel worker results.

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
    #
    # Every worker returns:
    #
    #     {
    #         "results": [structured_result]
    #     }
    #
    # operator.add combines those lists.
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
    FAN-OUT

    Create one Send object for every claim.
    """

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        print(
            f"Creating worker for {claim['claim_id']}"
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
    print("sends:\n",sends)
    return sends


# =============================================================
# 4. Claim worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process one claim.

    Each worker receives its own custom state and returns
    one structured result.
    """

    claim_id = state["claim_id"]
    claim_type = state["claim_type"]
    amount = state["amount"]

    print(
        f"\nWorker processing {claim_id}"
    )

    print(
        f"  Type   : {claim_type}"
    )

    print(
        f"  Amount : RM {amount}"
    )

    # ---------------------------------------------------------
    # Decision logic
    # ---------------------------------------------------------

    if amount <= 5000:

        decision = "APPROVED"

        reason = (
            "Amount is within approval limit"
        )

    elif amount <= 10000:

        decision = "REVIEW"

        reason = (
            "Amount requires additional review"
        )

    else:

        decision = "REJECTED"

        reason = (
            "Amount exceeds review threshold"
        )


    # ---------------------------------------------------------
    # Create structured result
    # ---------------------------------------------------------

    result = {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "amount": amount,
        "decision": decision,
        "reason": reason,
    }


    print(
        f"  Decision: {decision}"
    )


    # ---------------------------------------------------------
    # Return result
    #
    # The reducer will combine this list with the results
    # returned by other workers.
    # ---------------------------------------------------------

    return {
        "results": [result]
    }


# =============================================================
# 5. Build graph
# =============================================================

builder = StateGraph(
    OverallState
)


# Worker node
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
# 8. Compile
# =============================================================

graph = builder.compile()


# =============================================================
# 9. Input claims
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
]


# =============================================================
# 10. Run workflow
# =============================================================

print("=" * 60)
print("STARTING STRUCTURED FAN-OUT / FAN-IN")
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
        f"Decision : {item['decision']}"
    )

    print(
        f"Reason   : {item['reason']}"
    )


# =============================================================
# 12. Final summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    f"Input claims       : {len(claims)}"
)

print(
    f"Aggregated results : {len(result['results'])}"
)

print(
    "Fan-out             : 1 -> Many"
)

print(
    "Fan-in              : Many -> 1"
)

print(
    "Reducer             : operator.add"
)