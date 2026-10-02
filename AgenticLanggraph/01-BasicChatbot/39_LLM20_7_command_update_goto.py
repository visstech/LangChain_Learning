"""
===============================================================
LangGraph 20.7.1 - Command(update + goto)
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates how a LangGraph node can:

1. Update the graph state.
2. Dynamically choose the next node.

Instead of relying on a separate conditional edge,
the node returns a Command object.

Example:

    Command(
        update={"decision": "APPROVE"},
        goto="payment"
    )

LEARNING GOAL
-------------
Understand that Command can combine:

    STATE UPDATE
        +
    NEXT-NODE NAVIGATION

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
    payment_status: str


# =============================================================
# 2. Decision node
# =============================================================

def decide_expense(state: ExpenseState):

    print("\nDecision node")
    print(
        f"Employee: {state['employee']}"
    )
    print(
        f"Amount: RM {state['amount']}"
    )

    # ---------------------------------------------------------
    # For this first lesson, automatically approve
    # the expense.
    # ---------------------------------------------------------

    return Command(
        update={
            "decision": "APPROVE"
        },
        goto="payment"
    )


# =============================================================
# 3. Payment node
# =============================================================

def payment(state: ExpenseState):

    print("\nPayment node")

    print(
        f"Decision: {state['decision']}"
    )

    print(
        "Payment processed."
    )

    return {
        "payment_status": "PAID"
    }


# =============================================================
# 4. Build graph
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

builder.add_edge(
    START,
    "decide_expense"
)

builder.add_edge(
    "payment",
    END
)


# =============================================================
# 5. Compile graph
# =============================================================

graph = builder.compile()


# =============================================================
# 6. Run graph
# =============================================================

result = graph.invoke(
    {
        "employee": "senthil",
        "amount": 5000,
        "decision": "",
        "payment_status": ""
    }
)


# =============================================================
# 7. Display final state
# =============================================================

print("\n" + "=" * 60)
print("FINAL STATE")
print("=" * 60)

print(result)