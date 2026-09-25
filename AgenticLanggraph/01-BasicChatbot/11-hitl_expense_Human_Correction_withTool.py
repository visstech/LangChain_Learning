'''
This pattern is extremely important for production AI agents 
because tools may perform real-world actions such as:

submitting an insurance claim
approving a refund
sending an email
creating a ticket
updating a database
making a payment

We'll build it step by step, just like we've been doing.

Step 14.1 — Create a Payment Tool
'''


from typing import TypedDict
from langgraph.graph import START,END,StateGraph
from langgraph.types import interrupt,Command
from langgraph.checkpoint.memory import InMemorySaver

class ExpenseState(TypedDict):
    employee:str
    expense:str
    amount:float
    decision:str
    approval_required: bool
    manager_decision: str
    finance_decision: str
    corrected_amount: float

#Node 
def ExpenseRequest(state:ExpenseState):
    print("===Employee Expense===")
    print(f"Employee:{state['employee']}")
    print(f"Expense:{state['expense']}")
    print(f"Amount:{state['amount']}")
    print(f"decision:{state['decision']}")
    print(f"Approval Required:{state['approval_required']}")
    print(f"Manger Decision:{state['manager_decision']}")
    print(f"Finance Decision:{state['finance_decision']}")
    
    return state

def manager_approval(state: ExpenseState):
    decision  = interrupt(f"Manager approval required for RM:{state['amount']}" 
                          f"{state['expense']}."
                          f"Enter APPROVE or REJECT")
    decision = decision.strip().upper()
    if decision in ["APPROVE","REJECT"]:
        print(f"Manager decision:{decision}")
    return {"manager_decision":decision}

def finance_approval(state: ExpenseState):
    decision = interrupt(f"Finance Approval required for RM:{state['amount']}"
                         f"{state['expense']}."
                         f"Enter APPROVE or REJECT")
    decision = decision.strip().upper()
    if decision in ["APPROVE","REJECT"]:
            print(f"Finance decision:{decision}")
    return {"finance_decision":decision}
    
     
def Human_approval(state: ExpenseState):

    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:

        attempts += 1

        decision = interrupt(
            f"Approve expense of RM {state['amount']} "
            f"for {state['expense']}? "
            f"Enter APPROVE or REJECT."
        )

        decision = decision.strip().upper()

        if decision in ["APPROVE", "REJECT"]:
            print(f"Human decision: {decision}")

            return {
                "decision": decision
            }

        print(
            f"Invalid decision: {decision}. "
            f"Please enter APPROVE or REJECT."
        )
        
        if attempts == max_attempts:

            print("Maximum attempts reached. Expense rejected.")

            return {
                "decision": "REJECT"
            }
        
    
def process_expense(state: ExpenseState):
    print("✅ Expense approved!")
    print(
        f"Processing RM {state['amount']} "
        f"for {state['expense']}"
    )
    return state

def cancel_expense(state: ExpenseState):
    print("❌ Expense rejected.")
    print(
        f"Cancelled RM {state['amount']} "
        f"expense for {state['expense']}"
    )
    return state

def route_decision(state: ExpenseState):

    if state["decision"] == "APPROVE":
        return "process"

    return "cancel"


def check_amount(state: ExpenseState):
    if state["amount"] > 10000 :
        approval_required =True
    else:
        approval_required = False
    print(f"Amount : RM {state['amount']}")
    print(f"Approval required:{approval_required}")    
    return {"approval_required":approval_required}

def auto_approve(state: ExpenseState):

    print("✅ Expense automatically approved!")
    print(
        f"Auto-processing RM {state['amount']} "
        f"for {state['expense']}"
    )

    return {
        "decision": "APPROVE"
    }

def route_manager_decision(state: ExpenseState):  
    if state["manager_decision"] == "APPROVE":
        return "finance"

    return "reject"

def route_finance_decision(state: ExpenseState):
    if state["finance_decision"] == "APPROVE":
        return "process"

    return "reject"

def route_approval(state: ExpenseState):

    if state["approval_required"]:
        return "human"

    return "auto"

def human_correction(state: ExpenseState):
    corrected = interrupt(
        f"Review expense amount: RM {state['amount']}. "
        f"Enter the corrected amount, or enter ACCEPT."
    )

    corrected = corrected.strip().upper()

    if corrected == "ACCEPT":
        print(f"Human accepted amount: RM {state['amount']}")
        return {
            "corrected_amount": state["amount"]
        }

    try:
        corrected_amount = float(corrected)

        if corrected_amount <= 0:
            print("Invalid amount. Please enter a positive amount.")
            return {
                "corrected_amount": state["amount"]
            }

        print(f"Human corrected amount: RM {corrected_amount}")

        return {
            "corrected_amount": corrected_amount
        }

    except ValueError:
        print("Invalid amount. Keeping original amount.")
        return {
            "corrected_amount": state["amount"]
        }
    
def process_payment(amount: float, expense: str):
    print("💳 PAYMENT TOOL EXECUTED")
    print(f"Processing payment of RM {amount} for {expense}")

    return {
        "status": "SUCCESS",
        "amount": amount,
        "expense": expense
    }

def payment_node(state: ExpenseState):
    result = process_payment(
        state["amount"],
        state["expense"]
    )
    print(f"Payment result: {result}")
    return result
    
builder = StateGraph(ExpenseState)
builder.add_node("expenseRequest", ExpenseRequest)
builder.add_node("check_amount", check_amount)
builder.add_node("auto_approve", auto_approve)
builder.add_node("manager_approval", manager_approval)
builder.add_node("finance_approval", finance_approval)
builder.add_node("human_correction", human_correction)
builder.add_node("payment_node", payment_node)
builder.add_node("process_expense", process_expense)
builder.add_node("cancel_expense", cancel_expense)

builder.add_edge(START,"expenseRequest")
builder.add_edge("expenseRequest", "check_amount")

builder.add_conditional_edges(
    "check_amount",
    route_approval,
    {
        "human": "manager_approval",
        "auto": "auto_approve"
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

builder.add_edge("auto_approve", END)

builder.add_edge("process_expense", END)

builder.add_edge("cancel_expense", END)


memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)

config = {"configurable":{"thread_id":"test-001"}}

result = graph.invoke({
    "employee": "senthil",
    "expense": "Office Supplies",
    "amount": 12000,
    "decision": "",
    "approval_required": False,
    "manager_decision": "",
    "finance_decision": ""
}, config)

print(result)

result = graph.invoke(
    Command(resume="APPROVE"),
    config
)

print(result)

result = graph.invoke(
    Command(resume="REJECT"),
    config
)

print(result)


# ============================================================
# STEP 13 - HUMAN CORRECTION TEST
# ============================================================

correction_builder = StateGraph(ExpenseState)

correction_builder.add_node("human_correction", human_correction)
correction_builder.add_edge(START,"human_correction")
correction_builder.add_edge("human_correction",END)

correction_graph = correction_builder.compile(
    checkpointer=InMemorySaver()
)

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
        "corrected_amount": 0
    },
    correction_config
)

print(result)

result = correction_graph.invoke(
    Command(resume="4500"),
    correction_config
)

print(result)

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
        "corrected_amount": 0
    },
    accept_config
)

print(result)

result = correction_graph.invoke(
    Command(resume="ACCEPT"),
    accept_config
)

print(result)

def route_payment_decision(state: ExpenseState):
    if state["decision"] == "APPROVE":
        return "pay"

    return "reject"

#Creating tool graph
tool_builder = StateGraph(ExpenseState)
tool_builder.add_node("human_Approval",Human_approval)
tool_builder.add_node("payment_node",payment_node)
tool_builder.add_edge(START,"human_Approval")
tool_builder.add_conditional_edges("human_Approval",
    route_payment_decision,
    {
        "pay": "payment_node",
        "reject": END
    }
)

tool_builder.add_edge("payment_node", END)

tool_memory = InMemorySaver()
tool_graph = tool_builder.compile(checkpointer=tool_memory)
tool_config = {
    "configurable": {
        "thread_id": "payment-001"
    }
}

result = tool_graph.invoke(
    {
        "employee": "senthil",
        "expense": "Laptop",
        "amount": 5000,
        "decision": "",
        "approval_required": True,
        "manager_decision": "",
        "finance_decision": "",
        "corrected_amount": 0
    },
    tool_config
)
print(result)

result = tool_graph.invoke(
    Command(resume="APPROVE"),
    tool_config
)

print(result)

tool_config_reject = {
    "configurable": {
        "thread_id": "payment-002"
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
        "corrected_amount": 0
    },
    tool_config_reject
)

print(result)

result = tool_graph.invoke(
    Command(resume="REJECT"),
    tool_config_reject
)

print(result)