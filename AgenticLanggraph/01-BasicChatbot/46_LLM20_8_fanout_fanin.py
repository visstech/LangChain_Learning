"""
===============================================================
LangGraph 20.8.4 - Fan-out -> Fan-in
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates:

    FAN-OUT
        +
    FAN-IN
        +
    REDUCER

Workflow:

    Input Claims
         |
         v
      Dispatcher
         |
    +----+----+----+
    |    |    |    |
    v    v    v    v
  Worker Worker Worker Worker
    |    |    |    |
    +----+----+----+
         |
         v
    Results Aggregated
         |
         v
      Final State

FAN-OUT
-------
One input is dynamically split into multiple worker tasks
using Send.

FAN-IN
------
The results from multiple workers are combined into one
shared state field.

REDUCER
-------
The "results" state field uses operator.add so multiple
worker outputs are appended to the same list.

LEARNING GOAL
-------------
Understand the complete pattern:

    1 -> Many -> 1

This is the foundation of map-reduce workflows.

IMPORTANT
---------
The workers do not modify one another's state.

Each worker receives its own custom input.

The reducer combines the worker results into the main
graph state.

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
    #     {"results": ["some result"]}
    #
    # operator.add combines those lists.
    #
    # Example:
    #
    #     ["A"] + ["B"] + ["C"]
    #
    # becomes:
    #
    #     ["A", "B", "C"]
    # ---------------------------------------------------------

    results: Annotated[
        list[str],
        operator.add
    ]


# =============================================================
# 3. Dispatcher
# =============================================================

def dispatch_claims(state: OverallState):
    """
    FAN-OUT

    Create one Send object for each claim.
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

    return sends


# =============================================================
# 4. Claim worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process one claim.

    Each worker returns ONE result.

    The reducer will combine all worker results.
    """

    claim_id = state["claim_id"]
    claim_type = state["claim_type"]
    amount = state["amount"]

    print(
        f"\nWorker processing {claim_id}"
    )

    result = (
        f"{claim_id} processed | "
        f"Type={claim_type} | "
        f"Amount=RM {amount}"
    )

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
# 6. FAN-OUT
# =============================================================

builder.add_conditional_edges(
    START,
    dispatch_claims
)


# =============================================================
# 7. Worker completes its branch
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
# 9. Input data
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
        "amount": 12000,
    },
    {
        "claim_id": "CLM003",
        "claim_type": "Travel",
        "amount": 3000,
    },
]


# =============================================================
# 10. Execute graph
# =============================================================

print("=" * 60)
print("STARTING FAN-OUT -> FAN-IN WORKFLOW")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "results": [],
    }
)


# =============================================================
# 11. Display final state
# =============================================================

print("\n" + "=" * 60)
print("FINAL AGGREGATED RESULTS")
print("=" * 60)

for item in result["results"]:

    print(
        f"- {item}"
    )


# =============================================================
# 12. Final summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW COMPLETED")
print("=" * 60)

print(
    f"Input claims  : {len(claims)}"
)

print(
    f"Results       : {len(result['results'])}"
)

print(
    "Fan-out       : 1 -> Many"
)

print(
    "Fan-in        : Many -> 1"
)