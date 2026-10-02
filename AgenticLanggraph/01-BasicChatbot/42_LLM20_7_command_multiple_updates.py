"""
===============================================================
LangGraph 20.7.4 - Command with Multiple State Updates
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates how Command can:

1. Update multiple state fields.
2. Dynamically choose the next node.

The decision node will update:

    decision
    decision_reason
    approval_source

and then route to:

    payment
or
    rejection

LEARNING GOAL
-------------
Understand that Command(update=...) can update several
fields in graph state before navigating to another node.

===============================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command


# =============================================================
# 1. Define state
# =============================================================

class ExpenseState(TypedDict):
    employee: str
    amount: float
    decision: str
    decision_reason: str
    approval_source: str
    payment_status: str


# =============================================================
# 2. Decision node
# =============================================================

def decide_expense(state: ExpenseState):

    print("\nDecision node")
    print(f"Amount: RM {state['amount']}")

    if state["amount"] <= 5000:

        return Command(
            update={
                "decision": "APPROVE",
                "decision_reason": (
                    "Amount is within auto-approval limit"
                ),
                "approval_source": "SYSTEM",
            },
            goto="payment",
        )

    else:

        return Command(
            update={
                "decision": "REJECT",
                "decision_reason": (
                    "Amount exceeds auto-approval limit"
                ),
                "approval_source": "SYSTEM",
            },
            goto="rejection",
        )


# =============================================================
# 3. Payment node
# =============================================================

def payment(state: ExpenseState):

    print("\nPayment node")

    print(
        f"Decision reason: "
        f"{state['decision_reason']}"
    )

    print(
        f"Approval source: "
        f"{state['approval_source']}"
    )

    return {
        "payment_status": "PAID"
    }


# =============================================================
# 4. Rejection node
# =============================================================

def rejection(state: ExpenseState):

    print("\nRejection node")

    print(
        f"Decision reason: "
        f"{state['decision_reason']}"
    )

    print(
        f"Approval source: "
        f"{state['approval_source']}"
    )

    return {
        "payment_status": "NOT_PAID"
    }


# =============================================================
# 5. Build graph
# =============================================================

builder = StateGraph(ExpenseState)

builder.add_node(
    "decide_expense",
    decide_expense
)

builder.add_node(
    "payment",
    payment
)

builder.add_node(
    "rejection",
    rejection
)

builder.add_edge(
    START,
    "decide_expense"
)

builder.add_edge(
    "payment",
    END
)

builder.add_edge(
    "rejection",
    END
)


# =============================================================
# 6. Compile
# =============================================================

graph = builder.compile()


# =============================================================
# 7. Test approved expense
# =============================================================

print("=" * 60)
print("TEST 1 - APPROVED")
print("=" * 60)

result_1 = graph.invoke(
    {
        "employee": "senthil",
        "amount": 4000,
        "decision": "",
        "decision_reason": "",
        "approval_source": "",
        "payment_status": "",
    }
)

print("\nFinal State:")
print(result_1)


# =============================================================
# 8. Test rejected expense
# =============================================================

print("\n" + "=" * 60)
print("TEST 2 - REJECTED")
print("=" * 60)

result_2 = graph.invoke(
    {
        "employee": "senthil",
        "amount": 7000,
        "decision": "",
        "decision_reason": "",
        "approval_source": "",
        "payment_status": "",
    }
)

print("\nFinal State:")
print(result_2)