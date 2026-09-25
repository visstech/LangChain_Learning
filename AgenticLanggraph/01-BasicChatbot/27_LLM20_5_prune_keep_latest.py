from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from typing import TypedDict


# ============================================================
# 1. PostgreSQL connection
# ============================================================

DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


# ============================================================
# 2. State
# ============================================================

class ExpenseState(TypedDict):
    employee: str
    amount: float
    decision: str


# ============================================================
# 3. Human approval node
# ============================================================

def human_approval(state: ExpenseState):

    print("\n⏸️ Waiting for human approval...")

    response = interrupt(
        f"Approve expense of RM {state['amount']}?"
    )

    print(f"\nHuman response: {response}")

    return {
        "decision": response
    }


# ============================================================
# 4. Build graph
# ============================================================

builder = StateGraph(ExpenseState)

builder.add_node("human_approval", human_approval)

builder.add_edge(START, "human_approval")
builder.add_edge("human_approval", END)


# ============================================================
# 5. PostgreSQL checkpointer
# ============================================================

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    checkpointer.setup()

    graph = builder.compile(
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": "expense-002"
        }
    }


    # ========================================================
    # 6. Start workflow
    # ========================================================

    print("\n🚀 Starting workflow...")

    result = graph.invoke(
        {
            "employee": "Senthil",
            "amount": 12000,
            "decision": ""
        },
        config
    )

    print("\nAFTER INTERRUPT:")
    print(result)


    # ========================================================
    # 7. Resume workflow
    # ========================================================

    print("\n🔄 Resuming workflow...")

    result = graph.invoke(
        Command(resume="APPROVE"),
        config
    )

    print("\nFINAL STATE:")
    print(result)


    # ========================================================
    # 8. Show checkpoint history
    # ========================================================

    print("\n" + "=" * 60)
    print("CHECKPOINT HISTORY BEFORE PRUNE")
    print("=" * 60)

    history = list(
        graph.get_state_history(config)
    )

    for i, checkpoint in enumerate(history, start=1):

        print(f"\nCheckpoint {i}")
        print("Values:")
        print(checkpoint.values)

        print("Next:")
        print(checkpoint.next)

        print("Checkpoint ID:")
        print(
            checkpoint.config["configurable"]["checkpoint_id"]
        )


    # ========================================================
    # 9. Prune
    # ========================================================

    print("\n" + "=" * 60)
    print("🧹 PRUNING CHECKPOINT HISTORY")
    print("=" * 60)

    checkpointer.prune(
        ["expense-002"],
        strategy="keep_latest"
    )

    print("\n✅ Prune completed.")


    # ========================================================
    # 10. Show history after prune
    # ========================================================

    print("\n" + "=" * 60)
    print("CHECKPOINT HISTORY AFTER PRUNE")
    print("=" * 60)

    history_after = list(
        graph.get_state_history(config)
    )

    for i, checkpoint in enumerate(
        history_after,
        start=1
    ):

        print(f"\nCheckpoint {i}")
        print("Values:")
        print(checkpoint.values)

        print("Next:")
        print(checkpoint.next)

        print("Checkpoint ID:")
        print(
            checkpoint.config["configurable"]["checkpoint_id"]
        )