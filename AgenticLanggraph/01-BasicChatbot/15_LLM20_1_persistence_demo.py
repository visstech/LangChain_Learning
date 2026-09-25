from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver


# --------------------------------------------------
# 1. State
# --------------------------------------------------

class ExpenseState(TypedDict):
    employee: str
    amount: float
    decision: str


# --------------------------------------------------
# 2. Human approval
# --------------------------------------------------

def human_approval(state: ExpenseState):

    print("\n⏸️ Waiting for human approval...")

    response = interrupt(
        f"Approve expense of RM {state['amount']}?"
    )

    print(
        f"\nHuman response: {response}"
    )

    return {
        "decision": response
    }


# --------------------------------------------------
# 3. Build graph
# --------------------------------------------------

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


# --------------------------------------------------
# 4. In-memory checkpoint
# --------------------------------------------------

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


# --------------------------------------------------
# 5. Workflow ID
# --------------------------------------------------

config = {
    "configurable": {
        "thread_id": "expense-001"
    }
}


# --------------------------------------------------
# 6. Start workflow
# --------------------------------------------------

result = graph.invoke(
    {
        "employee": "Senthil",
        "amount": 5000,
        "decision": ""
    },
    config
)

print("\nAFTER INTERRUPT:")
print(result)


# --------------------------------------------------
# 7. Inspect checkpoint
# --------------------------------------------------

state = graph.get_state(config)

print("\nCHECKPOINT STATE:")
print("Values:", state.values)
print("Next:", state.next)