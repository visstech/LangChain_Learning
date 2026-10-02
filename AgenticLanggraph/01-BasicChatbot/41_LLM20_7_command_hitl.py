"""
===============================================================
LangGraph 20.7.3 - Command + Human-in-the-Loop
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program combines three LangGraph concepts:

1. Command(update=...)
2. Command(goto=...)
3. interrupt() for Human-in-the-Loop

WORKFLOW
--------
Small expense:
    Amount <= RM 5000
        ↓
    AUTO APPROVE
        ↓
    Payment

Large expense:
    Amount > RM 5000
        ↓
    Human Approval
        ↓
    APPROVE → Payment
    REJECT  → Rejection

LEARNING GOAL
-------------
Understand how a human decision can update graph state
and dynamically control which node executes next.

IMPORTANT
---------
interrupt() pauses the graph.

The graph must be compiled with a checkpointer when using
interrupt/resume across executions.

For this exercise we use InMemorySaver so the concept
remains simple.

===============================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver


# =============================================================
# 1. Define workflow state
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
    """
    Decide whether human approval is required.

    Small expense:
        AUTO APPROVE

    Large expense:
        Send workflow to human_approval.
    """

    print("\nDecision node")

    print(
        f"Employee: {state['employee']}"
    )

    print(
        f"Amount: RM {state['amount']}"
    )

    # ---------------------------------------------------------
    # Small expense
    # ---------------------------------------------------------

    if state["amount"] <= 5000:

        print(
            "Amount is within auto-approval limit."
        )

        return Command(
            update={
                "decision": "APPROVE"
            },
            goto="payment"
        )


    # ---------------------------------------------------------
    # Large expense
    # ---------------------------------------------------------

    print(
        "Human approval is required."
    )

    return Command(
        goto="human_approval"
    )


# =============================================================
# 3. Human approval node
# =============================================================

def human_approval(state: ExpenseState):
    """
    Pause the workflow and wait for human input.
    """

    print(
        "\n⏸️ Waiting for human approval..."
    )

    response = interrupt(
        {
            "message": (
                f"Approve expense of "
                f"RM {state['amount']}?"
            ),
            "options": [
                "APPROVE",
                "REJECT"
            ]
        }
    )

    # ---------------------------------------------------------
    # Human approved
    # ---------------------------------------------------------

    if response == "APPROVE":

        return Command(
            update={
                "decision": "APPROVE"
            },
            goto="payment"
        )


    # ---------------------------------------------------------
    # Human rejected
    # ---------------------------------------------------------

    return Command(
        update={
            "decision": "REJECT"
        },
        goto="rejection"
    )


# =============================================================
# 4. Payment node
# =============================================================

def payment(state: ExpenseState):

    print(
        "\nPayment node"
    )

    print(
        "Payment processed."
    )

    return {
        "payment_status": "PAID"
    }


# =============================================================
# 5. Rejection node
# =============================================================

def rejection(state: ExpenseState):

    print(
        "\nRejection node"
    )

    print(
        "Expense rejected."
    )

    return {
        "payment_status": "NOT_PAID"
    }


# =============================================================
# 6. Build graph
# =============================================================

builder = StateGraph(
    ExpenseState
)

builder.add_node(
    "decide_expense",
    decide_expense
)

builder.add_node(
    "human_approval",
    human_approval
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
# 7. Create checkpointer
# =============================================================

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


# =============================================================
# 8. Thread configuration
# =============================================================

config = {
    "configurable": {
        "thread_id": "command-hitl-001"
    }
}


# =============================================================
# 9. Start workflow
# =============================================================

print("=" * 60)
print("STARTING EXPENSE WORKFLOW")
print("=" * 60)

result = graph.invoke(
    {
        "employee": "senthil",
        "amount": 7000,
        "decision": "",
        "payment_status": ""
    },
    config
)


# =============================================================
# 10. Check whether workflow is interrupted
# =============================================================

print("\n" + "=" * 60)
print("WORKFLOW STATE")
print("=" * 60)

state = graph.get_state(config)

print(
    "Current state:"
)

print(
    state.values
)

print(
    "Next node:",
    state.next
)


# =============================================================
# 11. Resume with human decision
# =============================================================

print("\n" + "=" * 60)
print("RESUMING WITH HUMAN DECISION")
print("=" * 60)

result = graph.invoke(
    Command(
        resume="APPROVE"
    ),
    config
)


# =============================================================
# 12. Final state
# =============================================================

print("\n" + "=" * 60)
print("FINAL STATE")
print("=" * 60)

print(result)