from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.postgres import PostgresSaver


DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


class ExpenseState(TypedDict):
    employee: str
    amount: float
    decision: str


def human_approval(state: ExpenseState):

    response = interrupt(
        f"Approve expense of RM {state['amount']}?"
    )

    return {
        "decision": response
    }


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


with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    checkpointer.setup()

    graph = builder.compile(
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": "expense-001"
        }
    }

    print("\n📋 CHECKPOINT METADATA")
    print("=" * 60)

    history = graph.get_state_history(config)

    for i, checkpoint in enumerate(history, start=1):

        print(f"\nCheckpoint {i}")
        print("-" * 40)

        print("Values:")
        print(checkpoint.values)

        print("\nNext:")
        print(checkpoint.next)

        print("\nConfig:")
        print(checkpoint.config)

        print("\nMetadata:")
        print(checkpoint.metadata)