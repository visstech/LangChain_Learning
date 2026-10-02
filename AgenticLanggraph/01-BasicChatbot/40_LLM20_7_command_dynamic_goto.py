"""
===============================================================
LangGraph 20.7.2 - Command Dynamic goto
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates dynamic routing with Command.

The decision node will:

1. Inspect the expense amount.
2. Update the graph state.
3. Dynamically choose the next node.

RULE:
-----
Amount <= RM 5000
    -> APPROVE
    -> payment

Amount > RM 5000
    -> REJECT
    -> rejection

LEARNING GOAL
-------------
Understand how Command can combine:

    STATE UPDATE
        +
    DYNAMIC ROUTING

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
    print(f"Employee: {state['employee']}")
    print(f"Amount: RM {state['amount']}")

    # ---------------------------------------------------------
    # Dynamic routing
    # ---------------------------------------------------------

    if state["amount"] <= 5000:

        return Command(
            update={
                "decision": "APPROVE"
            },
            goto="payment"
        )

    else:

        return Command(
            update={
                "decision": "REJECT"
            },
            goto="rejection"
        )


# =============================================================
# 3. Payment node
# =============================================================

def payment(state: ExpenseState):

    print("\nPayment node")
    print("Payment processed.")

    return {
        "payment_status": "PAID"
    }


# =============================================================
# 4. Rejection node
# =============================================================

def rejection(state: ExpenseState):

    print("\nRejection node")
    print("Expense rejected.")

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
# 7. Test 1 - Approved expense
# =============================================================

print("\n" + "=" * 60)
print("TEST 1 - RM 5000")
print("=" * 60)

result_1 = graph.invoke(
    {
        "employee": "senthil",
        "amount": 5000,
        "decision": "",
        "payment_status": ""
    }
)

print("\nFinal State:")
print(result_1)


# =============================================================
# 8. Test 2 - Rejected expense
# =============================================================

print("\n" + "=" * 60)
print("TEST 2 - RM 7000")
print("=" * 60)

result_2 = graph.invoke(
    {
        "employee": "senthil",
        "amount": 7000,
        "decision": "",
        "payment_status": ""
    }
)

print("\nFinal State:")
print(result_2)