from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver


# ---------------------------------------------------------
# 1. Define the workflow state
# ---------------------------------------------------------
class ExpenseState(TypedDict):
    employee: str
    amount: float
    status: str


# ---------------------------------------------------------
# 2. Define a simple node
# ---------------------------------------------------------
def process_expense(state: ExpenseState):
    print(f"Processing expense for {state['employee']}")
    print(f"Amount: RM {state['amount']}")

    return {
        "status": "PROCESSED"
    }


# ---------------------------------------------------------
# 3. Build the graph
# ---------------------------------------------------------
builder = StateGraph(ExpenseState)

builder.add_node("process_expense", process_expense)

builder.add_edge(START, "process_expense")
builder.add_edge("process_expense", END)


# ---------------------------------------------------------
# 4. PostgreSQL connection
# ---------------------------------------------------------
DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


# ---------------------------------------------------------
# 5. Use PostgreSQL checkpointer
# ---------------------------------------------------------
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    graph = builder.compile(
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": "lifecycle-001"
        }
    }


    # -----------------------------------------------------
    # 6. Run the workflow
    # -----------------------------------------------------
    result = graph.invoke(
        {
            "employee": "senthil",
            "amount": 5000,
            "status": "NEW"
        },
        config
    )

    print("\nFinal State:")
    print(result)


    # -----------------------------------------------------
    # 7. Read checkpoint history
    # -----------------------------------------------------
    print("\nCheckpoint History:")

    history = list(
        graph.get_state_history(config)
    )

    for i, checkpoint in enumerate(history, start=1):

        print(f"\nCheckpoint {i}")
        print("Values:", checkpoint.values)
        print("Next:", checkpoint.next)

    # -----------------------------------------------------
    # 8. Delete completed thread
    # -----------------------------------------------------
    print("\nDeleting completed thread...")

    checkpointer.delete_thread(
        "lifecycle-001"
    )

    print("✅ Thread deleted.")


    # -----------------------------------------------------
    # 9. Verify deletion
    # -----------------------------------------------------
    print("\nVerifying thread cleanup...")

    history_after_delete = list(
        graph.get_state_history(config)
    )

    print(
        "Remaining checkpoints:",
        len(history_after_delete)
    )