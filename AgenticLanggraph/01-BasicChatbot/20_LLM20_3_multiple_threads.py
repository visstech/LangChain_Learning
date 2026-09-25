from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.postgres import PostgresSaver


# ============================================================
# 1. PostgreSQL connection
# ============================================================

DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl" # langgraph_hitl is database name
)


# ============================================================
# 2. State
# ============================================================

class ExpenseState(TypedDict):
    employee: str
    amount: float
    decision: str


# ============================================================
# 3. Human approval
# ============================================================

def human_approval(state: ExpenseState):

    print(
        f"\n⏸️ Waiting for approval: "
        f"{state['employee']} - RM {state['amount']}"
    )

    response = interrupt(
        f"Approve expense of RM {state['amount']}?"
    )

    return {
        "decision": response
    }


# ============================================================
# 4. Build graph
# ============================================================

builder = StateGraph(ExpenseState)

builder.add_node(
    "human_approval",
    human_approval
)

builder.add_edge(
    START,
    "human_approval"
)

builder.add_edge(
    "human_approval",
    END
)


# ============================================================
# 5. PostgreSQL checkpointer
# ============================================================

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    checkpointer.setup()

    graph = builder.compile(
        checkpointer=checkpointer
    )


    # ========================================================
    # Thread 1
    # ========================================================

    config_1 = {
        "configurable": {
            "thread_id": "expense-001"
        }
    }

    result_1 = graph.invoke(
        {
            "employee": "Senthil",
            "amount": 5000,
            "decision": ""
        },
        config_1
    )

    print("\nTHREAD 1:")
    print(result_1)


    # ========================================================
    # Thread 2
    # ========================================================

    config_2 = {
        "configurable": {
            "thread_id": "expense-002"
        }
    }

    result_2 = graph.invoke(
        {
            "employee": "Senthil",
            "amount": 12000,
            "decision": ""
        },
        config_2
    )

    print("\nTHREAD 2:")
    print(result_2)


    # ========================================================
    # Inspect Thread 1
    # ========================================================

    state_1 = graph.get_state(config_1)

    print("\nTHREAD 1 CHECKPOINT:")
    print("Values:", state_1.values)
    print("Next:", state_1.next)


    # ========================================================
    # Inspect Thread 2
    # ========================================================

    state_2 = graph.get_state(config_2)

    print("\nTHREAD 2 CHECKPOINT:")
    print("Values:", state_2.values)
    print("Next:", state_2.next)