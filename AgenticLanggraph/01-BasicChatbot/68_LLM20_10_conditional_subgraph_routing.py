"""
============================================================
68 - CONDITIONAL ROUTING BETWEEN MULTIPLE SUBGRAPHS
============================================================

WHAT THIS PROGRAM DOES
----------------------
This program demonstrates how a Parent Graph can conditionally
route a request to one of multiple specialized subgraphs.

We have:

1. Policy Subgraph
   - Handles policy-related requests.

2. Claims Subgraph
   - Handles claim-related requests.

3. Parent Graph
   - Determines which subgraph should execute.
   - Routes the request.
   - Receives the subgraph result.
   - Builds the final response.

PURPOSE
-------
In a real Agentic AI system, we should not execute every
available workflow for every user request.

Instead, the parent workflow should determine which
specialized component is required.

KEY CONCEPTS
------------
- Multiple Subgraphs
- Conditional Routing
- add_conditional_edges()
- Routing Function
- Specialized Responsibilities
- Parent Orchestration
- Modular Agent Architecture

EXPECTED FLOW
-------------

                         USER REQUEST
                              |
                              v
                       PARENT GRAPH
                              |
                              v
                      detect_request()
                              |
                    +---------+---------+
                    |                   |
                    v                   v
              POLICY REQUEST       CLAIM REQUEST
                    |                   |
                    v                   v
             POLICY SUBGRAPH      CLAIMS SUBGRAPH
                    |                   |
                    +---------+---------+
                              |
                              v
                       FINAL RESPONSE


IMPORTANT
---------
Only the required subgraph should execute.

For example:

"What is my policy status?"
        |
        +--> Policy Subgraph

"What is my claim status?"
        |
        +--> Claims Subgraph
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
    """

    print("Policy Subgraph: looking up policy...")

    customer_id = state["customer_id"]

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

policy_builder.add_node(
    "policy_lookup",
    policy_lookup,
)

policy_builder.add_edge(
    START,
    "policy_lookup",
)

policy_builder.add_edge(
    "policy_lookup",
    END,
)

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
    """

    print("Claims Subgraph: looking up claim...")

    claim_id = state["claim_id"]

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

claims_builder.add_node(
    "claim_lookup",
    claim_lookup,
)

claims_builder.add_edge(
    START,
    "claim_lookup",
)

claims_builder.add_edge(
    "claim_lookup",
    END,
)

claims_graph = claims_builder.compile()


# ============================================================
# 3. PARENT STATE
# ============================================================

class ParentState(TypedDict):
    customer_id: str
    claim_id: str
    user_message: str

    route: str

    policy_status: str
    policy_expiry: str

    claim_status: str
    claim_amount: float

    final_response: str


# ============================================================
# 4. REQUEST DETECTION / ROUTING FUNCTION
# ============================================================

def detect_request(state: ParentState):
    """
    Determine which specialized subgraph should handle
    the user's request.

    This example uses simple keyword detection.

    Later, this can be replaced by an LLM-based intent
    classifier.
    """

    message = state["user_message"].lower()

    print()
    print("Parent Graph: detecting request type...")

    if "policy" in message:
        route = "policy"

    elif "claim" in message:
        route = "claim"

    else:
        route = "unknown"

    print(f"Parent Graph: selected route -> {route}")

    return {
        "route": route
    }


# ============================================================
# 5. POLICY SUBGRAPH NODE
# ============================================================

def call_policy_subgraph(state: ParentState):
    """
    Invoke the Policy Subgraph.
    """

    print("Parent Graph: calling Policy Subgraph...")

    result = policy_graph.invoke(
        {
            "customer_id": state["customer_id"],
            "policy_status": "UNKNOWN",
            "policy_expiry": "UNKNOWN",
        }
    )

    return {
        "policy_status": result["policy_status"],
        "policy_expiry": result["policy_expiry"],
    }


# ============================================================
# 6. CLAIMS SUBGRAPH NODE
# ============================================================

def call_claims_subgraph(state: ParentState):
    """
    Invoke the Claims Subgraph.
    """

    print("Parent Graph: calling Claims Subgraph...")

    result = claims_graph.invoke(
        {
            "claim_id": state["claim_id"],
            "claim_status": "UNKNOWN",
            "claim_amount": 0.0,
        }
    )

    return {
        "claim_status": result["claim_status"],
        "claim_amount": result["claim_amount"],
    }


# ============================================================
# 7. FINAL RESPONSE
# ============================================================

def build_final_response(state: ParentState):
    """
    Build a response based on the selected route.
    """

    print("Parent Graph: building final response...")

    if state["route"] == "policy":

        response = (
            f"Customer {state['customer_id']} | "
            f"Policy Status: {state['policy_status']} | "
            f"Expiry: {state['policy_expiry']}"
        )

    elif state["route"] == "claim":

        response = (
            f"Claim {state['claim_id']} | "
            f"Status: {state['claim_status']} | "
            f"Amount: RM{state['claim_amount']:.2f}"
        )

    else:

        response = (
            "Sorry, I could not determine whether your "
            "request is related to a policy or a claim."
        )

    return {
        "final_response": response
    }


# ============================================================
# 8. BUILD PARENT GRAPH
# ============================================================

parent_builder = StateGraph(ParentState)

parent_builder.add_node(
    "detect_request",
    detect_request,
)

parent_builder.add_node(
    "call_policy_subgraph",
    call_policy_subgraph,
)

parent_builder.add_node(
    "call_claims_subgraph",
    call_claims_subgraph,
)

parent_builder.add_node(
    "build_final_response",
    build_final_response,
)


# ============================================================
# 9. CONDITIONAL ROUTING
# ============================================================

def route_request(state: ParentState):
    """
    Return the node that should execute next.
    """

    if state["route"] == "policy":
        return "call_policy_subgraph"

    elif state["route"] == "claim":
        return "call_claims_subgraph"

    else:
        return "build_final_response"


parent_builder.add_edge(
    START,
    "detect_request",
)


parent_builder.add_conditional_edges(
    "detect_request",
    route_request,
    {
        "call_policy_subgraph": "call_policy_subgraph",
        "call_claims_subgraph": "call_claims_subgraph",
        "build_final_response": "build_final_response",
    },
)


parent_builder.add_edge(
    "call_policy_subgraph",
    "build_final_response",
)

parent_builder.add_edge(
    "call_claims_subgraph",
    "build_final_response",
)

parent_builder.add_edge(
    "build_final_response",
    END,
)


parent_graph = parent_builder.compile()


# ============================================================
# 10. TEST 1 - POLICY REQUEST
# ============================================================

print()
print("=" * 60)
print("68 - CONDITIONAL ROUTING BETWEEN MULTIPLE SUBGRAPHS")
print("=" * 60)

print()
print("-" * 60)
print("TEST 1 - POLICY REQUEST")
print("-" * 60)

policy_result = parent_graph.invoke(
    {
        "customer_id": "CUST001",
        "claim_id": "CLM001",
        "user_message": "What is my policy status?",

        "route": "",

        "policy_status": "UNKNOWN",
        "policy_expiry": "UNKNOWN",

        "claim_status": "UNKNOWN",
        "claim_amount": 0.0,

        "final_response": "",
    }
)

print()
print("Policy Result:")
print(policy_result)


# ============================================================
# 11. TEST 2 - CLAIM REQUEST
# ============================================================

print()
print("-" * 60)
print("TEST 2 - CLAIM REQUEST")
print("-" * 60)

claim_result = parent_graph.invoke(
    {
        "customer_id": "CUST001",
        "claim_id": "CLM001",
        "user_message": "What is the status of my claim?",

        "route": "",

        "policy_status": "UNKNOWN",
        "policy_expiry": "UNKNOWN",

        "claim_status": "UNKNOWN",
        "claim_amount": 0.0,

        "final_response": "",
    }
)

print()
print("Claim Result:")
print(claim_result)


# ============================================================
# 12. TEST 3 - UNKNOWN REQUEST
# ============================================================

print()
print("-" * 60)
print("TEST 3 - UNKNOWN REQUEST")
print("-" * 60)

unknown_result = parent_graph.invoke(
    {
        "customer_id": "CUST001",
        "claim_id": "CLM001",
        "user_message": "Tell me something about my account",

        "route": "",

        "policy_status": "UNKNOWN",
        "policy_expiry": "UNKNOWN",

        "claim_status": "UNKNOWN",
        "claim_amount": 0.0,

        "final_response": "",
    }
)

print()
print("Unknown Result:")
print(unknown_result)


print()
print("=" * 60)
print("CONDITIONAL SUBGRAPH ROUTING DEMONSTRATION COMPLETED")
print("=" * 60)