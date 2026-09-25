from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict


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


# NEW InMemorySaver
checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


config = {
    "configurable": {
        "thread_id": "expense-001"
    }
}


print("\nTrying to resume previous workflow...")

result = graph.invoke(
    Command(resume="APPROVE"),
    config
)

print("\nRESUME RESULT:")
print(result)