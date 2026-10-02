"""
===============================================================
LangGraph 20.6.5 - Actual PostgreSQL Checkpoint Cleanup
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates ACTUAL deletion of a LangGraph
checkpoint thread from PostgreSQL.

It will:

1. Create two real workflow threads.
2. Persist their checkpoints in PostgreSQL.
3. Display their checkpoint history.
4. Delete ONLY the approved thread.
5. Verify that the deleted thread has no checkpoints.
6. Verify that the other thread is still present.

IMPORTANT
---------
delete_thread(thread_id)

removes the LangGraph checkpoint history associated with that
specific thread.

It does NOT delete other thread histories.

PRODUCTION LESSON
-----------------
A cleanup job should first identify and review deletion
candidates.

Only an explicitly approved thread should be deleted.

===============================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver


# =============================================================
# 1. Workflow state
# =============================================================

class ExpenseState(TypedDict):
    employee: str
    amount: float
    status: str


# =============================================================
# 2. Workflow node
# =============================================================

def process_expense(state: ExpenseState):

    print(
        f"Processing expense for "
        f"{state['employee']}"
    )

    return {
        "status": "PROCESSED"
    }


# =============================================================
# 3. Build graph
# =============================================================

builder = StateGraph(ExpenseState)

builder.add_node(
    "process_expense",
    process_expense
)

builder.add_edge(
    START,
    "process_expense"
)

builder.add_edge(
    "process_expense",
    END
)


# =============================================================
# 4. PostgreSQL configuration
# =============================================================

DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


# =============================================================
# 5. Create PostgreSQL checkpointer
# =============================================================

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    graph = builder.compile(
        checkpointer=checkpointer
    )


    # =========================================================
    # 6. Create two real threads
    # =========================================================

    thread_a = {
        "configurable": {
            "thread_id": "cleanup-real-001"
        }
    }

    thread_b = {
        "configurable": {
            "thread_id": "cleanup-real-002"
        }
    }


    # =========================================================
    # 7. Run thread A
    # =========================================================

    graph.invoke(
        {
            "employee": "senthil",
            "amount": 5000,
            "status": "NEW"
        },
        thread_a
    )


    # =========================================================
    # 8. Run thread B
    # =========================================================

    graph.invoke(
        {
            "employee": "arun",
            "amount": 3000,
            "status": "NEW"
        },
        thread_b
    )


    # =========================================================
    # 9. Verify both threads
    # =========================================================

    history_a = list(
        graph.get_state_history(thread_a)
    )

    history_b = list(
        graph.get_state_history(thread_b)
    )

    print("\n" + "=" * 60)
    print("BEFORE CLEANUP")
    print("=" * 60)

    print(
        f"cleanup-real-001 checkpoints: "
        f"{len(history_a)}"
    )

    print(
        f"cleanup-real-002 checkpoints: "
        f"{len(history_b)}"
    )


    # =========================================================
    # 10. Select ONE approved cleanup candidate
    # =========================================================

    approved_thread_id = "cleanup-real-001"

    print("\nApproved cleanup thread:")
    print(approved_thread_id)


    # =========================================================
    # 11. Delete ONLY approved thread
    # =========================================================

    print("\nDeleting approved thread...")

    checkpointer.delete_thread(
        approved_thread_id
    )

    print("✅ Thread deleted.")


    # =========================================================
    # 12. Verify deleted thread
    # =========================================================

    history_a_after = list(
        graph.get_state_history(thread_a)
    )

    print("\nDeleted thread verification:")

    print(
        f"cleanup-real-001 checkpoints remaining: "
        f"{len(history_a_after)}"
    )


    # =========================================================
    # 13. Verify other thread still exists
    # =========================================================

    history_b_after = list(
        graph.get_state_history(thread_b)
    )

    print("\nOther thread verification:")

    print(
        f"cleanup-real-002 checkpoints remaining: "
        f"{len(history_b_after)}"
    )


    # =========================================================
    # 14. Final result
    # =========================================================

    print("\n" + "=" * 60)
    print("CLEANUP RESULT")
    print("=" * 60)

    if (
        len(history_a_after) == 0
        and len(history_b_after) > 0
    ):
        print(
            "✅ cleanup-real-001 was deleted."
        )

        print(
            "✅ cleanup-real-002 was preserved."
        )

        print(
            "✅ Thread-level cleanup verified."
        )
    else:
        print(
            "⚠️ Cleanup verification failed."
        )