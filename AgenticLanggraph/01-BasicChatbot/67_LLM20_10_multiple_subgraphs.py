"""
============================================================
67 - MULTIPLE SUBGRAPHS IN A PARENT WORKFLOW
============================================================

WHAT THIS PROGRAM DOES
----------------------
This program demonstrates how a parent LangGraph workflow
can orchestrate multiple specialized subgraphs.

We create:

1. Policy Subgraph
   - Looks up customer policy information.

2. Claims Subgraph
   - Looks up claim information.

3. Parent Workflow
   - Calls both subgraphs.
   - Combines their results.
   - Builds a final insurance response.

PURPOSE
-------
The purpose of this lesson is to understand how multiple
specialized subgraphs can be combined into one larger
workflow.

KEY CONCEPTS
------------
- Multiple Subgraphs
- Parent Graph
- Specialized Responsibilities
- State Mapping
- Subgraph Invocation
- Modular Architecture
- Workflow Orchestration

EXPECTED FLOW
-------------

                 PARENT WORKFLOW
                       |
             +---------+---------+
             |                   |
             v                   v
      POLICY SUBGRAPH      CLAIMS SUBGRAPH
             |                   |
             v                   v
       Policy Details       Claim Details
             |                   |
             +---------+---------+
                       |
                       v
                Final Response


IMPORTANT
---------
Each subgraph has its own state schema.

The parent graph does not directly manipulate the internal
logic of the subgraphs.

The parent simply:

1. Sends required input.
2. Receives the result.
3. Combines the results.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. POLICY SUBGRAPH
# ============================================================

class PolicyState(TypedDict):
    customer_id: str
    policy_status: str
    policy_expiry: str


def policy_lookup(state: PolicyState):
    """
    Simulate a policy lookup.

    In a real application this could call:
    - PostgreSQL
    - REST API
    - Insurance database
    - Policy service
    """

    print("Policy Subgraph: looking up policy...")

    customer_id = state["customer_id"]

    # Simulated policy database
    policies = {
        "CUST001": {
            "policy_status": "ACTIVE",
            "policy_expiry": "2026-12-31",
        },
        "CUST002": {
            "policy_status": "EXPIRED",
            "policy_expiry": "2025-12-31",
        },
    }

    policy = policies.get(
        customer_id,
        {
            "policy_status": "NOT_FOUND",
            "policy_expiry": "UNKNOWN",
        },
    )

    return {
        "policy_status": policy["policy_status"],
        "policy_expiry": policy["policy_expiry"],
    }


policy_builder = StateGraph(PolicyState)

policy_builder.add_node("policy_lookup", policy_lookup)

policy_builder.add_edge(START, "policy_lookup")
policy_builder.add_edge("policy_lookup", END)

policy_graph = policy_builder.compile()


# ============================================================
# 2. CLAIMS SUBGRAPH
# ============================================================

class ClaimsState(TypedDict):
    claim_id: str
    claim_status: str
    claim_amount: float


def claim_lookup(state: ClaimsState):
    """
    Simulate a claim lookup.

    In a real application this could call:
    - Claims database
    - Claims API
    - Claims service
    """

    print("Claims Subgraph: looking up claim...")

    claim_id = state["claim_id"]

    # Simulated claims database
    claims = {
        "CLM001": {
            "claim_status": "UNDER_REVIEW",
            "claim_amount": 5000.0,
        },
        "CLM002": {
            "claim_status": "APPROVED",
            "claim_amount": 2500.0,
        },
        "CLM003": {
            "claim_status": "REJECTED",
            "claim_amount": 3000.0,
        },
    }

    claim = claims.get(
        claim_id,
        {
            "claim_status": "NOT_FOUND",
            "claim_amount": 0.0,
        },
    )

    return {
        "claim_status": claim["claim_status"],
        "claim_amount": claim["claim_amount"],
    }


claims_builder = StateGraph(ClaimsState)

claims_builder.add_node("claim_lookup", claim_lookup)

claims_builder.add_edge(START, "claim_lookup")
claims_builder.add_edge("claim_lookup", END)

claims_graph = claims_builder.compile()


# ============================================================
# 3. PARENT WORKFLOW STATE
# ============================================================

class ParentState(TypedDict):
    customer_id: str
    claim_id: str

    policy_status: str
    policy_expiry: str

    claim_status: str
    claim_amount: float

    final_response: str


# ============================================================
# 4. PARENT NODE - CALL POLICY SUBGRAPH
# ============================================================

def get_policy_information(state: ParentState):
    """
    Call the Policy Subgraph.

    Notice that the parent state and policy state are
    different.

    We explicitly map the required fields.
    """

    print("Parent Workflow: calling Policy Subgraph...")

    policy_result = policy_graph.invoke(
        {
            "customer_id": state["customer_id"],
            "policy_status": "UNKNOWN",
            "policy_expiry": "UNKNOWN",
        }
    )

    return {
        "policy_status": policy_result["policy_status"],
        "policy_expiry": policy_result["policy_expiry"],
    }


# ============================================================
# 5. PARENT NODE - CALL CLAIMS SUBGRAPH
# ============================================================

def get_claim_information(state: ParentState):
    """
    Call the Claims Subgraph.

    Again, the parent explicitly maps its state into the
    Claims Subgraph state.
    """

    print("Parent Workflow: calling Claims Subgraph...")

    claim_result = claims_graph.invoke(
        {
            "claim_id": state["claim_id"],
            "claim_status": "UNKNOWN",
            "claim_amount": 0.0,
        }
    )

    return {
        "claim_status": claim_result["claim_status"],
        "claim_amount": claim_result["claim_amount"],
    }


# ============================================================
# 6. PARENT NODE - BUILD FINAL RESPONSE
# ============================================================

def build_final_response(state: ParentState):
    """
    Combine the results returned by both subgraphs.
    """

    print("Parent Workflow: combining subgraph results...")

    response = (
        f"Customer {state['customer_id']} | "
        f"Policy: {state['policy_status']} | "
        f"Expiry: {state['policy_expiry']} | "
        f"Claim {state['claim_id']} | "
        f"Status: {state['claim_status']} | "
        f"Amount: RM{state['claim_amount']:.2f}"
    )

    return {
        "final_response": response
    }


# ============================================================
# 7. BUILD PARENT GRAPH
# ============================================================

parent_builder = StateGraph(ParentState)

parent_builder.add_node(
    "get_policy_information",
    get_policy_information,
)

parent_builder.add_node(
    "get_claim_information",
    get_claim_information,
)

parent_builder.add_node(
    "build_final_response",
    build_final_response,
)


# ============================================================
# 8. DEFINE PARENT WORKFLOW
# ============================================================

parent_builder.add_edge(
    START,
    "get_policy_information",
)

parent_builder.add_edge(
    "get_policy_information",
    "get_claim_information",
)

parent_builder.add_edge(
    "get_claim_information",
    "build_final_response",
)

parent_builder.add_edge(
    "build_final_response",
    END,
)


parent_graph = parent_builder.compile()


# ============================================================
# 9. RUN THE PARENT WORKFLOW
# ============================================================

print()
print("=" * 60)
print("67 - MULTIPLE SUBGRAPHS IN A PARENT WORKFLOW")
print("=" * 60)

result = parent_graph.invoke(
    {
        "customer_id": "CUST001",
        "claim_id": "CLM001",

        "policy_status": "UNKNOWN",
        "policy_expiry": "UNKNOWN",

        "claim_status": "UNKNOWN",
        "claim_amount": 0.0,

        "final_response": "",
    }
)


# ============================================================
# 10. DISPLAY FINAL RESULT
# ============================================================

print()
print("=" * 60)
print("FINAL RESULT")
print("=" * 60)

print(result)

print()
print("=" * 60)
print("FINAL RESPONSE")
print("=" * 60)

print(result["final_response"])

print()
print("=" * 60)
print("MULTIPLE SUBGRAPHS DEMONSTRATION COMPLETED")
print("=" * 60)