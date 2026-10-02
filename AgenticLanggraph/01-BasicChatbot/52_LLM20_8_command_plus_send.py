"""
===============================================================
LangGraph 20.8.10 - Combining Send + Command
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program combines:

    Command
        +
    Send
        +
    Reducer

The dispatcher:

1. Receives multiple claims.
2. Creates one Send for each claim.
3. Updates the graph state with the number of branches.
4. Uses Command.goto to launch the Send objects.

LEARNING GOAL
-------------
Understand this pattern:

    Command(
        update={...},
        goto=[
            Send(...),
            Send(...),
            Send(...)
        ]
    )

In other words:

    update state
        +
    dynamically fan-out

===============================================================
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, Send


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
    # State updated by dispatcher
    # ---------------------------------------------------------
    branch_count: int

    # ---------------------------------------------------------
    # Multiple workers update this field.
    # Reducer combines all result lists.
    # ---------------------------------------------------------
    results: Annotated[
        list[dict],
        operator.add
    ]


# =============================================================
# 3. Dispatcher
# =============================================================

def dispatcher(state: OverallState):
    """
    Create dynamic Send objects and return them through
    Command.goto.

    Command performs TWO jobs:

        1. Update branch_count
        2. Fan-out using Send
    """

    print("\nDispatcher started.")

    sends = []

    for claim in state["claims"]:

        claim_id = claim["claim_id"]
        claim_type = claim["claim_type"]
        amount = claim["amount"]

        print(
            f"Creating Send for {claim_id}"
        )

        sends.append(
            Send(
                "claim_worker",
                {
                    "claim_id": claim_id,
                    "claim_type": claim_type,
                    "amount": amount,
                }
            )
        )

    print(
        f"Total Send objects created: {len(sends)}"
    )

    # ---------------------------------------------------------
    # Command does TWO things here:
    #
    # 1. update graph state
    # 2. goto multiple Send destinations
    # ---------------------------------------------------------

    return Command(
        update={
            "branch_count": len(sends)
        },
        goto=sends
    )


# =============================================================
# 4. Worker
# =============================================================

def claim_worker(state: ClaimWorkerState):
    """
    Process one claim.

    Every worker receives its own custom state.
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

    result = {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "amount": amount,
        "status": "PROCESSED",
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


# Dispatcher node
builder.add_node(
    "dispatcher",
    dispatcher
)


# Worker node
builder.add_node(
    "claim_worker",
    claim_worker
)


# =============================================================
# 6. START -> Dispatcher
# =============================================================

builder.add_edge(
    START,
    "dispatcher"
)


# =============================================================
# 7. Worker -> END
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
# 10. Run graph
# =============================================================

print("=" * 60)
print("COMMAND + SEND WORKFLOW")
print("=" * 60)

result = graph.invoke(
    {
        "claims": claims,
        "branch_count": 0,
        "results": [],
    }
)


# =============================================================
# 11. Display final state
# =============================================================

print("\n" + "=" * 60)
print("FINAL STATE")
print("=" * 60)

print(
    f"Branch count : {result['branch_count']}"
)

print(
    f"Result count : {len(result['results'])}"
)


# =============================================================
# 12. Display aggregated results
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
        f"Status   : {item['status']}"
    )


# =============================================================
# 13. Final summary
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW SUMMARY")
print("=" * 60)

print(
    "Command      : update + goto"
)

print(
    "Goto type    : multiple Send objects"
)

print(
    "Fan-out      : 1 -> Many"
)

print(
    "Fan-in       : Many -> 1"
)

print(
    "Reducer      : operator.add"
)