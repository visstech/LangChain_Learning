"""
HITL + Tools + Conditional Routing + Structured Human Responses

This example demonstrates:

Step 2  - Basic Human Approval
Step 3  - Conditional Routing
Step 4  - Multiple Human Approvals
Step 5  - Human Correction
Step 6  - HITL + Tool
Step 7  - Human Correction + Tool
Step 8  - Conditional HITL + Tool
Step 17 - Structured Human Responses
"""

from typing import TypedDict

from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver


# ============================================================
# STATE
# ============================================================

class ExpenseState(TypedDict):
    employee: str
    expense: str
    amount: float
    decision: str
    approval_required: bool
    manager_decision: str
    finance_decision: str
    corrected_amount: float
    approval_comment: str


# ============================================================
# BASIC EXPENSE REQUEST
# ============================================================

def ExpenseRequest(state: ExpenseState):

    print("=== Employee Expense ===")
    print(f"Employee: {state['employee']}")
    print(f"Expense: {state['expense']}")
    print(f"Amount: {state['amount']}")
    print(f"Decision: {state['decision']}")
    print(f"Approval Required: {state['approval_required']}")
    print(f"Manager Decision: {state['manager_decision']}")
    print(f"Finance Decision: {state['finance_decision']}")

    return state


# ============================================================
# MANAGER APPROVAL
# ============================================================

def manager_approval(state: ExpenseState):

    decision = interrupt(
        f"Manager approval required for RM {state['amount']} "
        f"for {state['expense']}. "
        f"Enter APPROVE or REJECT."
    )

    decision = decision.strip().upper()

    if decision in ["APPROVE", "REJECT"]:
        print(f"Manager decision: {decision}")

    return {
        "manager_decision": decision
    }


# ============================================================
# FINANCE APPROVAL
# ============================================================

def finance_approval(state: ExpenseState):

    decision = interrupt(
        f"Finance approval required for RM {state['amount']} "
        f"for {state['expense']}. "
        f"Enter APPROVE or REJECT."
    )

    decision = decision.strip().upper()

    if decision in ["APPROVE", "REJECT"]:
        print(f"Finance decision: {decision}")

    return {
        "finance_decision": decision
    }


# ============================================================
# HUMAN APPROVAL
# STEP 17 - STRUCTURED HUMAN RESPONSE
# ============================================================

def Human_approval(state: ExpenseState):

    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:

        attempts += 1

        response = interrupt(
            {
                "message": (
                    f"Approve expense of RM {state['amount']} "
                    f"for {state['expense']}?"
                ),
                "options": ["APPROVE", "REJECT"],
                "required_fields": [
                    "decision",
                    "comment"
                ]
            }
        )

        # ----------------------------------------------------
        # STEP 17:
        # Response is expected to be a dictionary
        #
        # {
        #     "decision": "APPROVE",
        #     "comment": "Required for project"
        # }
        # ----------------------------------------------------

        decision = response["decision"].strip().upper()
        comment = response["comment"].strip()

        if decision in ["APPROVE", "REJECT"]:

            print(f"Human decision: {decision}")
            print(f"Approval comment: {comment}")

            return {
                "decision": decision,
                "approval_comment": comment
            }

        print(
            f"Invalid decision: {decision}. "
            f"Please enter APPROVE or REJECT."
        )

        if attempts == max_attempts:

            print("Maximum attempts reached. Expense rejected.")

            return {
                "decision": "REJECT",
                "approval_comment": "Maximum attempts reached"
            }


# ============================================================
# PROCESS EXPENSE
# ============================================================

def process_expense(state: ExpenseState):

    print("✅ Expense approved!")

    print(
        f"Processing RM {state['amount']} "
        f"for {state['expense']}"
    )

    return state


# ============================================================
# CANCEL EXPENSE
# ============================================================

def cancel_expense(state: ExpenseState):

    print("❌ Expense rejected.")

    print(
        f"Cancelled RM {state['amount']} "
        f"expense for {state['expense']}"
    )

    return state


# ============================================================
# ROUTE DECISION
# ============================================================

def route_decision(state: ExpenseState):

    if state["decision"] == "APPROVE":
        return "process"

    return "cancel"


# ============================================================
# CHECK AMOUNT
# ============================================================

def check_amount(state: ExpenseState):

    if state["amount"] > 10000:
        approval_required = True
    else:
        approval_required = False

    print(f"Amount: RM {state['amount']}")
    print(f"Approval required: {approval_required}")

    return {
        "approval_required": approval_required
    }


# ============================================================
# AUTO APPROVAL
# ============================================================

def auto_approve(state: ExpenseState):

    print("✅ Expense automatically approved!")

    print(
        f"Auto-processing RM {state['amount']} "
        f"for {state['expense']}"
    )

    return {
        "decision": "APPROVE"
    }


# ============================================================
# ROUTE MANAGER DECISION
# ============================================================

def route_manager_decision(state: ExpenseState):

    if state["manager_decision"] == "APPROVE":
        return "finance"

    return "reject"


# ============================================================
# ROUTE FINANCE DECISION
# ============================================================

def route_finance_decision(state: ExpenseState):

    if state["finance_decision"] == "APPROVE":
        return "process"

    return "reject"


# ============================================================
# ROUTE APPROVAL
# ============================================================

def route_approval(state: ExpenseState):

    if state["approval_required"]:
        return "human"

    return "auto"


# ============================================================
# HUMAN CORRECTION
# ============================================================

def human_correction(state: ExpenseState):

    corrected = interrupt(
        f"Review expense amount: RM {state['amount']}. "
        f"Enter the corrected amount, or enter ACCEPT."
    )

    corrected = corrected.strip().upper()

    if corrected == "ACCEPT":

        print(
            f"Human accepted amount: RM {state['amount']}"
        )

        return {
            "corrected_amount": state["amount"]
        }

    try:

        corrected_amount = float(corrected)

        if corrected_amount <= 0:

            print(
                "Invalid amount. "
                "Please enter a positive amount."
            )

            return {
                "corrected_amount": state["amount"]
            }

        print(
            f"Human corrected amount: RM "
            f"{corrected_amount}"
        )

        return {
            "corrected_amount": corrected_amount
        }

    except ValueError:

        print(
            "Invalid amount. "
            "Keeping original amount."
        )

        return {
            "corrected_amount": state["amount"]
        }


# ============================================================
# PAYMENT TOOL
# ============================================================

def process_payment(amount: float, expense: str):

    print("💳 PAYMENT TOOL EXECUTED")

    print(
        f"Processing payment of RM {amount} "
        f"for {expense}"
    )

    return {
        "status": "SUCCESS",
        "amount": amount,
        "expense": expense
    }


# ============================================================
# PAYMENT NODE
# ============================================================

def payment_node(state: ExpenseState):

    result = process_payment(
        state["amount"],
        state["expense"]
    )

    print(f"Payment result: {result}")

    return result


# ============================================================
# CORRECTED PAYMENT TOOL
# ============================================================

def process_corrected_payment(
    amount: float,
    expense: str
):

    print("💳 CORRECTED PAYMENT TOOL EXECUTED")

    print(
        f"Processing corrected payment of RM {amount} "
        f"for {expense}"
    )

    return {
        "status": "SUCCESS",
        "amount": amount,
        "expense": expense
    }


# ============================================================
# CORRECTED PAYMENT NODE
# ============================================================

def corrected_payment_node(state: ExpenseState):

    result = process_corrected_payment(
        state["corrected_amount"],
        state["expense"]
    )

    print(
        f"Corrected payment result: {result}"
    )

    return {
        "decision": "APPROVE"
    }


# ============================================================
# CHECK CORRECTED AMOUNT
# ============================================================

def check_corrected_amount(state: ExpenseState):

    if state["corrected_amount"] > 1000:

        print(
            f"Corrected amount "
            f"RM {state['corrected_amount']} "
            f"requires human approval."
        )

        return {
            "approval_required": True
        }

    print(
        f"Corrected amount "
        f"RM {state['corrected_amount']} "
        f"does not require human approval."
    )

    return {
        "approval_required": False
    }


# ============================================================
# ROUTE CORRECTED AMOUNT
# ============================================================

def route_corrected_amount(state: ExpenseState):

    if state["approval_required"]:
        return "human_Approval"

    return "auto_approve"


# ============================================================
# ROUTE PAYMENT DECISION
# ============================================================

def route_payment_decision(state: ExpenseState):

    if state["decision"] == "APPROVE":
        return "pay"

    return "reject"


# ============================================================
# GRAPH 1
# BASIC MULTI-LEVEL APPROVAL
# ============================================================

builder = StateGraph(ExpenseState)

#Actual functions are connected when you register the nodes:
# Here expenseRequest node name and ExpenseRequest is the connected function name.
builder.add_node(
    "expenseRequest",
    ExpenseRequest
)

builder.add_node(
    "check_amount",
    check_amount
)

builder.add_node(
    "auto_approve",
    auto_approve
)

builder.add_node(
    "manager_approval",
    manager_approval
)

builder.add_node(
    "finance_approval",
    finance_approval
)

builder.add_node(
    "process_expense",
    process_expense
)

builder.add_node(
    "cancel_expense",
    cancel_expense
)


builder.add_edge(
    START,
    "expenseRequest"
)

builder.add_edge(
    "expenseRequest",
    "check_amount"
)


builder.add_conditional_edges(
    "check_amount",   # Source node: where we are
    route_approval,    # Routing function: decides where to go
    {
        "human": "manager_approval",   # If route_approval returns "human"
                                       # → go to manager_approval node 
                                       
        "auto": "auto_approve"         # If route_approval returns "auto"
                                      # → go to auto_approve node
    }
)


builder.add_conditional_edges(
    "manager_approval",
    route_manager_decision,
    {
        "finance": "finance_approval",
        "reject": "cancel_expense"
    }
)


builder.add_conditional_edges(
    "finance_approval",
    route_finance_decision,
    {
        "process": "process_expense",
        "reject": "cancel_expense"
    }
)


builder.add_edge(
    "auto_approve",
    END
)

builder.add_edge(
    "process_expense",
    END
)

builder.add_edge(
    "cancel_expense",
    END
)


memory = InMemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# ============================================================
# GRAPH 2
# HUMAN CORRECTION
# ============================================================

correction_builder = StateGraph(ExpenseState)

correction_builder.add_node(
    "human_correction",
    human_correction
)

correction_builder.add_edge(
    START,
    "human_correction"
)

correction_builder.add_edge(
    "human_correction",
    END
)


correction_graph = correction_builder.compile(
    checkpointer=InMemorySaver()
)


# ============================================================
# GRAPH 3
# HUMAN APPROVAL + PAYMENT TOOL
# ============================================================

tool_builder = StateGraph(ExpenseState)

tool_builder.add_node(
    "human_Approval",
    Human_approval
)

tool_builder.add_node(
    "payment_node",
    payment_node
)

tool_builder.add_edge(
    START,
    "human_Approval"
)

tool_builder.add_conditional_edges(
    "human_Approval",
    route_payment_decision,
    {
        "pay": "payment_node",
        "reject": END
    }
)

tool_builder.add_edge(
    "payment_node",
    END
)


tool_memory = InMemorySaver()

tool_graph = tool_builder.compile(
    checkpointer=tool_memory
)


# ============================================================
# GRAPH 4
# HUMAN CORRECTION + CONDITIONAL APPROVAL + PAYMENT
# ============================================================

correction_tool_builder = StateGraph(ExpenseState)


correction_tool_builder.add_node(
    "human_correction",
    human_correction
)

correction_tool_builder.add_node(
    "check_corrected_amount",
    check_corrected_amount
)

correction_tool_builder.add_node(
    "human_Approval",
    Human_approval
)

correction_tool_builder.add_node(
    "corrected_payment_node",
    corrected_payment_node
)


# START → HUMAN CORRECTION

correction_tool_builder.add_edge(
    START,
    "human_correction"
)


# HUMAN CORRECTION → CHECK CORRECTED AMOUNT

correction_tool_builder.add_edge(
    "human_correction",
    "check_corrected_amount"
)


# CHECK CORRECTED AMOUNT → CONDITIONAL ROUTING

correction_tool_builder.add_conditional_edges(
    "check_corrected_amount",
    route_corrected_amount,
    {
        "human_Approval": "human_Approval",
        "auto_approve": "corrected_payment_node"
    }
)


# HUMAN APPROVAL → PAYMENT OR END

correction_tool_builder.add_conditional_edges(
    "human_Approval",
    route_payment_decision,
    {
        "pay": "corrected_payment_node",
        "reject": END
    }
)


# PAYMENT → END

correction_tool_builder.add_edge(
    "corrected_payment_node",
    END
)


correction_tool_memory = InMemorySaver()

correction_tool_graph = correction_tool_builder.compile(
    checkpointer=correction_tool_memory
)


# ============================================================
# STEP 17
# STRUCTURED HUMAN RESPONSE TEST
# ============================================================

print("\n")
print("=" * 60)
print("STEP 17 - STRUCTURED HUMAN RESPONSE")
print("=" * 60)


step17_config = {
    "configurable": {
        "thread_id": "step17-001"
    }
}


# ------------------------------------------------------------
# START
# ------------------------------------------------------------

result = tool_graph.invoke(
    {
        "employee": "senthil",
        "expense": "Laptop",
        "amount": 5000,
        "decision": "",
        "approval_required": True,
        "manager_decision": "",
        "finance_decision": "",
        "corrected_amount": 0,
        "approval_comment": ""
    },
    step17_config
)

print(result)


# ------------------------------------------------------------
# HUMAN RESPONSE
# ------------------------------------------------------------

result = tool_graph.invoke(
    Command(
        resume={
            "decision": "APPROVE",
            "comment": "Required for the project"
        }
    ),
    step17_config
)

print(result)


# ============================================================
# STEP 17 - REJECT TEST
# ============================================================

print("\n")
print("=" * 60)
print("STEP 17 - STRUCTURED REJECTION")
print("=" * 60)


step17_reject_config = {
    "configurable": {
        "thread_id": "step17-002"
    }
}


result = tool_graph.invoke(
    {
        "employee": "senthil",
        "expense": "Mobile",
        "amount": 3000,
        "decision": "",
        "approval_required": True,
        "manager_decision": "",
        "finance_decision": "",
        "corrected_amount": 0,
        "approval_comment": ""
    },
    step17_reject_config
)

print(result)


result = tool_graph.invoke(
    Command(
        resume={
            "decision": "REJECT",
            "comment": "Not required for the project"
        }
    ),
    step17_reject_config
)

print(result)


# ============================================================
# STEP 16 - HUMAN CORRECTION TEST
# ============================================================

print("\n")
print("=" * 60)
print("STEP 16 - HUMAN CORRECTION")
print("=" * 60)


correction_config = {
    "configurable": {
        "thread_id": "correction-001"
    }
}


result = correction_graph.invoke(
    {
        "employee": "senthil",
        "expense": "Laptop",
        "amount": 5000,
        "decision": "",
        "approval_required": False,
        "manager_decision": "",
        "finance_decision": "",
        "corrected_amount": 0,
        "approval_comment": ""
    },
    correction_config
)

print(result)


result = correction_graph.invoke(
    Command(resume="4500"),
    correction_config
)

print(result)


# ============================================================
# STEP 16 - ACCEPT ORIGINAL AMOUNT
# ============================================================

accept_config = {
    "configurable": {
        "thread_id": "correction-002"
    }
}


result = correction_graph.invoke(
    {
        "employee": "senthil",
        "expense": "Mouse",
        "amount": 150,
        "decision": "",
        "approval_required": False,
        "manager_decision": "",
        "finance_decision": "",
        "corrected_amount": 0,
        "approval_comment": ""
    },
    accept_config
)

print(result)


result = correction_graph.invoke(
    Command(resume="ACCEPT"),
    accept_config
)

print(result)


# ============================================================
# STEP 16.7 - AUTO APPROVAL AFTER CORRECTION
# ============================================================

print("\n")
print("=" * 60)
print("STEP 16.7 - AUTO APPROVAL AFTER CORRECTION")
print("=" * 60)


auto_config = {
    "configurable": {
        "thread_id": "correction-payment-003"
    }
}


result = correction_tool_graph.invoke(
    {
        "employee": "senthil",
        "expense": "Mouse",
        "amount": 5000,
        "decision": "",
        "approval_required": True,
        "manager_decision": "",
        "finance_decision": "",
        "corrected_amount": 0,
        "approval_comment": ""
    },
    auto_config
)

print(result)


# Human correction is still a STRING

result = correction_tool_graph.invoke(
    Command(resume="800"),
    auto_config
)

print(result)


# ============================================================
# STEP 16.8 - REJECT AFTER HUMAN CORRECTION
# ============================================================

print("\n")
print("=" * 60)
print("STEP 16.8 - REJECT AFTER HUMAN CORRECTION")
print("=" * 60)


reject_config = {
    "configurable": {
        "thread_id": "correction-payment-004"
    }
}


result = correction_tool_graph.invoke(
    {
        "employee": "senthil",
        "expense": "Laptop",
        "amount": 5000,
        "decision": "",
        "approval_required": True,
        "manager_decision": "",
        "finance_decision": "",
        "corrected_amount": 0,
        "approval_comment": ""
    },
    reject_config
)

print(result)


# Human correction → STRING

result = correction_tool_graph.invoke(
    Command(resume="4500"),
    reject_config
)

print(result)


# Human approval → STRUCTURED RESPONSE

result = correction_tool_graph.invoke(
    Command(
        resume={
            "decision": "REJECT",
            "comment": "Expense is not justified"
        }
    ),
    reject_config
)

print(result)