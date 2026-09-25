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

#Node 
def ExpenseRequest(state:ExpenseState):
    print("===Employee Expense===")
    print(f"Employee:{state['employee']}")
    print(f"Expense:{state['expense']}")
    print(f"Amount:{state['amount']}")
    print(f"decision:{state['decision']}")
    return state

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
    
    
builder = StateGraph(ExpenseState)
builder.add_node('Check_amount',check_amount)
builder.add_node('expenseRequest',ExpenseRequest)
builder.add_node("human_Approval",Human_approval)
builder.add_node("process_expense",process_expense)
builder.add_node("cancel_expense",cancel_expense)
builder.add_edge(START,'expenseRequest')
builder.add_edge('expenseRequest',"human_Approval")
builder.add_conditional_edges(
    "human_Approval",
    route_decision,
    {
        "process": "process_expense",
        "cancel": "cancel_expense"
    }
)
builder.add_edge("process_expense", END)
builder.add_edge("cancel_expense", END)


memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)

config = {"configurable":{"thread_id":"expense-001"}}
result = graph.invoke({"employee":"senthil",
                       "expense":"Laptop",
                       "amount":5000,
                       "decision":""},
                       config    
                          )
state_snapshot = graph.get_state(config)

print("Current State:")
print(state_snapshot.values)

print("\nNext:")
print(state_snapshot.next)

#Approve the Human decision 
result = graph.invoke(Command(resume="APPROVE"),config)
print(result)

config = {"configurable":{"thread_id":"expense-002"}}
result = graph.invoke({"employee":"senthil",
                       "expense":"Laptop",
                       "amount":5000,
                       "decision":""},
                       config    
                          )
result = graph.invoke(Command(resume="REJECT"),config)
print(result)

config = {"configurable":{"thread_id":"expense-003"}}
result = graph.invoke({"employee":"senthil",
                       "expense":"Laptop",
                       "amount":5000,
                       "decision":""},
                       config    
                          )
result = graph.invoke(Command(resume="MAYBE"),config)
print(result)
result = graph.invoke(Command(resume="NO"),config)
print(result)
result = graph.invoke(Command(resume="yes"),config)
print(result)
state_snapshot = graph.get_state(config)
print('======Current state is===========\n')
print('value is:',state_snapshot.values)
print('Next is:',state_snapshot.next)