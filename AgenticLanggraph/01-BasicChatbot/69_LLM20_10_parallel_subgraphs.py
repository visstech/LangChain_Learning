
"""
Lesson 69: Parallel Subgraphs in LangGraph

Purpose:
    Run two independent subgraphs from the same parent graph:
    1. Policy Subgraph
    2. Claims Subgraph

Key concepts:
    - StateGraph and TypedDict
    - Compiling reusable subgraphs
    - Fan-out: starting independent branches
    - Fan-in: waiting for both branches
    - Parent state updates from child graph results

Expected flow:
    START
      |----> Policy Subgraph ----|
      |                          |----> Build Final Response --> END
      |----> Claims Subgraph ----|

Expected result:
    Customer: CUST001
    Policy: ACTIVE
    Expiry: 2026-12-31
    Claim: CLM001
    Status: UNDER_REVIEW
    Amount: RM5000.00

Note:
    The policy and claim data below are simulated.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ============================================================
# STEP 1: DEFINE POLICY SUBGRAPH STATE
# ============================================================

class PolicyState(TypedDict):
    customer_id: str
    policy_status: str
    policy_expiry: str


# ============================================================
# STEP 2: DEFINE CLAIMS SUBGRAPH STATE
# ============================================================

class ClaimsState(TypedDict):
    claim_id: str
    claim_status: str
    claim_amount: float


# ============================================================
# STEP 3: DEFINE PARENT GRAPH STATE
# ============================================================

class ParentState(TypedDict):
    customer_id: str
    claim_id: str

    # Results returned by the Policy Subgraph
    policy_status: str
    policy_expiry: str

    # Results returned by the Claims Subgraph
    claim_status: str
    claim_amount: float

    # Final combined response
    final_response: str


# ============================================================
# STEP 4: BUILD THE POLICY SUBGRAPH
# ============================================================

def get_policy(state: PolicyState) -> dict:
    """Simulate retrieving a customer's policy information."""

    print("Policy Subgraph: retrieving policy information...")

    return {
        "policy_status": "ACTIVE",
        "policy_expiry": "2026-12-31",
    }


policy_builder = StateGraph(PolicyState)

policy_builder.add_node("get_policy", get_policy)

policy_builder.add_edge(START, "get_policy")
policy_builder.add_edge("get_policy", END)

policy_graph = policy_builder.compile()


# ============================================================
# STEP 5: BUILD THE CLAIMS SUBGRAPH
# ============================================================

def get_claim(state: ClaimsState) -> dict:
    """Simulate retrieving a claim's information."""

    print("Claims Subgraph: retrieving claim information...")

    return {
        "claim_status": "UNDER_REVIEW",
        "claim_amount": 5000.00,
    }


claims_builder = StateGraph(ClaimsState)

claims_builder.add_node("get_claim", get_claim)

claims_builder.add_edge(START, "get_claim")
claims_builder.add_edge("get_claim", END)

claims_graph = claims_builder.compile()


# ============================================================
# STEP 6: CREATE PARENT GRAPH NODES
# ============================================================

def get_policy_information(state: ParentState) -> dict:
    """Call the compiled Policy Subgraph."""

    policy_result = policy_graph.invoke(
        {"customer_id": state["customer_id"]}
    )

    return {
        "policy_status": policy_result["policy_status"],
        "policy_expiry": policy_result["policy_expiry"],
    }


def get_claim_information(state: ParentState) -> dict:
    """Call the compiled Claims Subgraph."""

    claim_result = claims_graph.invoke(
        {"claim_id": state["claim_id"]}
    )

    return {
        "claim_status": claim_result["claim_status"],
        "claim_amount": claim_result["claim_amount"],
    }


def build_final_response(state: ParentState) -> dict:
    """Combine the results returned by both subgraphs."""

    response = (
        f"Customer: {state['customer_id']} | "
        f"Policy: {state['policy_status']} | "
        f"Expiry: {state['policy_expiry']} | "
        f"Claim: {state['claim_id']} | "
        f"Status: {state['claim_status']} | "
        f"Amount: RM{state['claim_amount']:.2f}"
    )

    return {"final_response": response}


# ============================================================
# STEP 7: BUILD THE PARENT GRAPH
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

# FAN-OUT:
# Both independent branches start from START.
parent_builder.add_edge(START, "get_policy_information")
parent_builder.add_edge(START, "get_claim_information")

# FAN-IN:
# The final response node waits for BOTH branches.
parent_builder.add_edge(
    ["get_policy_information", "get_claim_information"],
    "build_final_response",
)

parent_builder.add_edge("build_final_response", END)

parent_graph = parent_builder.compile()


# ============================================================
# STEP 8: EXECUTE THE GRAPH
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("LESSON 69: PARALLEL SUBGRAPHS")
    print("=" * 65)

    initial_state = {
        "customer_id": "CUST001",
        "claim_id": "CLM001",
    }

    result = parent_graph.invoke(initial_state)

    print("\nFINAL RESPONSE")
    print("-" * 65)
    print(result["final_response"])
    print("-" * 65)
