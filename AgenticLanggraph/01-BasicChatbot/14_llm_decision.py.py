from typing import TypedDict
from pydantic import BaseModel, Field
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. Define the LangGraph State
# ============================================================

class ExpenseState(TypedDict):
    employee: str
    expense: str
    amount: float
    approval_required: str
    decision_reason: str
    decision: str
    payment_status: str


# ============================================================
# 2. Define the structured LLM response
# ============================================================

class ExpenseDecision(BaseModel):

    decision: str = Field(
        description="Either HUMAN_REQUIRED or AUTO_APPROVE"
    )

    reason: str = Field(
        description="Short explanation for the decision"
    )


# ============================================================
# 3. Create the LLM
# ============================================================

llm = ChatOllama(
    model="llama3",
    temperature=0
)


# ============================================================
# 4. Create structured LLM
# ============================================================

structured_llm = llm.with_structured_output(
    ExpenseDecision
)


# ============================================================
# 5. LLM Decision Node
# ============================================================

def llm_decision(state: ExpenseState):

    prompt = f"""
You are an expense approval assistant.

Analyze the following expense:

Employee: {state['employee']}
Expense: {state['expense']}
Amount: RM {state['amount']}

Decide whether this expense requires human approval.

Rules:
- High-value or potentially sensitive expenses should require human approval.
- Small routine expenses may not require human approval.

Return:
- HUMAN_REQUIRED when human approval is needed.
- AUTO_APPROVE when human approval is not needed.
- Provide a short reason for the decision.
"""

    decision = structured_llm.invoke(prompt)

    print("\nStructured LLM Decision:")
    print("Decision:", decision.decision)
    print("Reason:", decision.reason)

    return {
        "approval_required": decision.decision,
        "decision_reason": decision.reason
    }

def validate_decision(state: ExpenseState):

    decision = state["approval_required"]

    allowed_decisions = {
        "HUMAN_REQUIRED",
        "AUTO_APPROVE"
    }

    if decision not in allowed_decisions:

        print(
            f"\n⚠️ Invalid LLM decision: {decision}"
        )

        print(
            "Safely stopping the workflow."
        )

        return {
            "approval_required": "INVALID"
        }

    print(
        f"\n✅ Valid LLM decision: {decision}"
    )

    return {}

def invalid_decision(state: ExpenseState):

    print(
        "\n🛑 Workflow stopped because "
        "the LLM decision was invalid."
    )

    return {}

# ============================================================
# 6. Routing Function
# ============================================================

def route_decision(state: ExpenseState):

    decision = state["approval_required"]

    if decision == "HUMAN_REQUIRED":
        return "human"

    if decision == "AUTO_APPROVE":
        return "auto"

    return "invalid"


# ============================================================
# 7. Human Approval Node
# ============================================================

def human_approval(state: ExpenseState):

    print("\n⏸️ HUMAN APPROVAL REQUIRED")

    print(
        f"Expense: {state['expense']}"
    )

    print(
        f"Amount: RM {state['amount']}"
    )

    print(
        f"Reason: {state['decision_reason']}"
    )

    response = interrupt(
        {
            "message": (
                f"Approve expense of RM "
                f"{state['amount']}?"
            ),
            "options": [
                "APPROVE",
                "REJECT"
            ]
        }
    )

    decision = response.strip().upper()

    print(
        f"\nHuman Decision: {decision}"
    )

    return {
        "decision": decision
    }

# ============================================================
# 8. Auto Approval Node
# ============================================================

def auto_approve(state: ExpenseState):

    print("\n➡️ Routing to AUTO APPROVAL")
    print("Reason:", state["decision_reason"])

    return {}

def process_payment(state: ExpenseState):

    if state["decision"] != "APPROVE":

        print(
            "\n🛑 PAYMENT BLOCKED"
        )

        print(
            "Payment requires explicit human approval."
        )

        return {
            "payment_status": "BLOCKED"
        }

    print(
        "\n💰 PAYMENT TOOL EXECUTED"
    )

    print(
        f"Employee: {state['employee']}"
    )

    print(
        f"Expense: {state['expense']}"
    )

    print(
        f"Amount Paid: RM {state['amount']}"
    )

    return {
        "payment_status": "PAID"
    }

def route_after_human_approval(state: ExpenseState):

    if state["decision"] == "APPROVE":
        return "payment"

    return "end"

# ============================================================
# 9. Build Graph
# ============================================================

builder = StateGraph(ExpenseState)


builder.add_node(
    "llm_decision",
    llm_decision
)

builder.add_node(
    "human_approval",
    human_approval
)

builder.add_node(
    "auto_approve",
    auto_approve
)

builder.add_node(
    "validate_decision",
    validate_decision
)

builder.add_node(
    "invalid_decision",
    invalid_decision
)

builder.add_node(
    "process_payment",
    process_payment
)

# ============================================================
# 10. Graph Edges
# ============================================================

builder.add_edge(
    START,
    "llm_decision"
)

builder.add_edge(
    "llm_decision",
    "validate_decision"
)

builder.add_conditional_edges(
    "validate_decision",
    route_decision,
    {
        "human": "human_approval",
        "auto": "auto_approve",
        "invalid": "invalid_decision"
    }
)

builder.add_conditional_edges(
    "human_approval",
    route_after_human_approval,
    {
        "payment": "process_payment",
        "end": END
    }
)

builder.add_edge(
    "human_approval",
    END
)

builder.add_edge(
    "auto_approve",
    END
)

builder.add_edge(
    "invalid_decision",
    END
)
builder.add_edge(
    "process_payment",
    END
)
# ============================================================
# 11. Compile
# ============================================================

graph = builder.compile()


# ============================================================
# 12. Test
# ============================================================

result = graph.invoke(
    {
        "employee": "Senthil",
        "expense": "Office pen",
        "amount": 20,
        "approval_required": "",
        "decision_reason": ""
    }
)


print("\nFinal State:")
print(result)

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)

config = {
    "configurable": {
        "thread_id": "expense-001"
    }
}

result = graph.invoke(
    {
        "employee": "Senthil",
        "expense": "Laptop",
        "amount": 5000,
        "approval_required": "",
        "decision_reason": "",
        "decision": ""
    },
    config
)

print("\nAFTER FIRST INVOKE:")
print(result)

result = graph.invoke(
    Command(resume="REJECT"),
    config
)

print("\nAFTER HUMAN APPROVAL:")
print(result)