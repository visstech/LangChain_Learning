from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
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

    print(
        f"\n⏸️ Waiting for approval: "
        f"{state['employee']} - RM {state['amount']}"
    )

    response = interrupt(
        f"Approve expense of RM {state['amount']}?"
    )

    print(f"\nHuman response: {response}")

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


    # ========================================================
    # Thread 1
    # ========================================================

    config_1 = {
        "configurable": {
            "thread_id": "expense-001"
        }
    }


    print("\n🔄 Resuming Thread 1...")

    result_1 = graph.invoke(
        Command(resume="APPROVE"),
        config_1
    )

    print("\nTHREAD 1 FINAL STATE:")
    print(result_1)


    # ========================================================
    # Thread 2
    # ========================================================

    config_2 = {
        "configurable": {
            "thread_id": "expense-002"
        }
    }


    state_2 = graph.get_state(config_2)

    print("\nTHREAD 2 CURRENT STATE:")

    print("Values:", state_2.values)
    print("Next:", state_2.next)