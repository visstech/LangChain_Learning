
"""
Lesson 70: Parallel Subgraphs with Reducers in LangGraph

Purpose:
    Execute Policy and Claims subgraphs in parallel and combine
    their results into one shared list in the parent graph.

Key concepts:
    1. Parallel branches and fan-out/fan-in
    2. Annotated state fields
    3. The operator.add reducer
    4. Combining multiple updates to the same state key
    5. Building a final response from aggregated results

Expected flow:
    START
      |----> Policy Subgraph ----|
      |                          |----> Aggregate Results --> END
      |----> Claims Subgraph ----|

Important:
    Both parent branches update the same "findings" state key.
    The reducer combines their list updates rather than replacing
    one branch's findings with the other branch's findings.

    This example uses simulated insurance data.
"""

import operator
from typing import Annotated, TypedDict

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

    # The reducer combines list updates from parallel branches.
    findings: Annotated[list[str], operator.add]

    final_response: str


# ============================================================
# STEP 4: BUILD THE POLICY SUBGRAPH
# ============================================================

def get_policy(state: PolicyState) -> dict:
    """Simulate retrieving policy information."""

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
    """Simulate retrieving claim information."""

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
# STEP 6: CREATE THE PARENT GRAPH BRANCHES
# ============================================================

def get_policy_information(state: ParentState) -> dict:
    """Call Policy Subgraph and contribute one finding."""

    result = policy_graph.invoke(
        {"customer_id": state["customer_id"]}
    )

    finding = (
        f"Policy: {result['policy_status']} | "
        f"Expiry: {result['policy_expiry']}"
    )

    # This list update is combined with other branch updates
    # by the operator.add reducer.
    return {"findings": [finding]}


def get_claim_information(state: ParentState) -> dict:
    """Call Claims Subgraph and contribute one finding."""

    result = claims_graph.invoke(
        {"claim_id": state["claim_id"]}
    )

    finding = (
        f"Claim: {state['claim_id']} | "
        f"Status: {result['claim_status']} | "
        f"Amount: RM{result['claim_amount']:.2f}"
    )

    # This update targets the SAME key as the policy branch.
    return {"findings": [finding]}


# ============================================================
# STEP 7: BUILD THE FINAL RESPONSE
# ============================================================

def build_final_response(state: ParentState) -> dict:
    """Combine all findings after both branches complete."""

    # Sort only to make the displayed output deterministic.
    # The reducer itself is responsible for accumulating results.
    ordered_findings = sorted(state["findings"])

    response = (
        f"Customer: {state['customer_id']} | "
        + " | ".join(ordered_findings)
    )

    return {"final_response": response}


# ============================================================
# STEP 8: BUILD THE PARENT GRAPH
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

# FAN-OUT: schedule both branches from START.
parent_builder.add_edge(START, "get_policy_information")
parent_builder.add_edge(START, "get_claim_information")

# FAN-IN: wait for both branches before aggregating.
parent_builder.add_edge(
    ["get_policy_information", "get_claim_information"],
    "build_final_response",
)

parent_builder.add_edge("build_final_response", END)

parent_graph = parent_builder.compile()


# ============================================================
# STEP 9: RUN THE GRAPH
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("LESSON 70: PARALLEL SUBGRAPHS WITH REDUCERS")
    print("=" * 65)

    initial_state = {
        "customer_id": "CUST001",
        "claim_id": "CLM001",
        "findings": [],
    }

    result = parent_graph.invoke(initial_state)

    print("\nAGGREGATED FINDINGS")
    print("-" * 65)

    for finding in result["findings"]:
        print(f"- {finding}")

    print("\nFINAL RESPONSE")
    print("-" * 65)
    print(result["final_response"])
    print("-" * 65)
