from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from typing import TypedDict


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

builder.add_node("human_approval", human_approval)

builder.add_edge(START, "human_approval")
builder.add_edge("human_approval", END)


with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    checkpointer.setup()

    graph = builder.compile(
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": "expense-run-test"
        }
    }

    print("\n🚀 Starting workflow...")

    result = graph.invoke(
        {
            "employee": "Senthil",
            "amount": 3000,
            "decision": ""
        },
        config
    )

    print("\nRESULT:")
    print(result)

    print("\nCONFIG AFTER INVOKE:")
    print(config)

    print("\nCHECKPOINT STATE CONFIG:")

    state = graph.get_state(config)

    print(state.config)