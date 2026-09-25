from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver


# ============================================================
# STATE
# ============================================================

class ExpenseState(TypedDict):
    employee: str
    amount: float
    decision: str


# ============================================================
# HUMAN APPROVAL NODE
# ============================================================

def human_approval(state:ExpenseState):

    print("\n⏸️ Waiting for human approval...")

    response = interrupt(
        f"Approve expense of RM {state['amount']}"
    )

    print(f"Human response {response}")

    return {
        "decision": response
    }


# ============================================================
# GRAPH
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
# CHECKPOINTER
# ============================================================

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


# ============================================================
# THREAD 1
# ============================================================

config_1 = {
    "configurable": {
        "thread_id": "expense-001"
    }
}

result_1 = graph.invoke(
    {
        "employee": "senthil",
        "amount": 5000,
        "decision": ""
    },
    config_1
)

state_1 = graph.get_state(config_1)

print("\n============================================================")
print("THREAD 1 CHECKPOINT STATE")
print("============================================================")

print("Values:", state_1.values)
print("Next:", state_1.next)

print("\nTHREAD 1 PAUSED:")
print(result_1)


# ============================================================
# THREAD 2
# ============================================================

config_2 = {
    "configurable": {
        "thread_id": "expense-002"
    }
}

result_2 = graph.invoke(
    {
        "employee": "senthil",
        "amount": 3000,
        "decision": ""
    },
    config_2
)
state_2 = graph.get_state(config_2)

print("\n============================================================")
print("THREAD 2 CHECKPOINT STATE")
print("============================================================")

print("Values:", state_2.values)
print("Next:", state_2.next)

print("\nTHREAD 2 PAUSED:")
print(result_2)


# ============================================================
# RESUME THREAD 1
# ============================================================

result_1 = graph.invoke(
    Command(resume="APPROVE"),
    config_1
)

print("\nTHREAD 1 AFTER RESUME:")
print(result_1)


# ============================================================
# RESUME THREAD 2
# ============================================================

result_2 = graph.invoke(
    Command(resume="REJECT"),
    config_2
)

print("\nTHREAD 2 AFTER RESUME:")
print(result_2)