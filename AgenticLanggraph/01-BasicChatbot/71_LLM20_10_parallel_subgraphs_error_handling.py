
"""
LESSON 71: PARALLEL SUBGRAPHS WITH ERROR HANDLING AND PARTIAL RESULTS

PURPOSE:
    Learn how to handle failures in parallel LangGraph subgraphs
    without losing successful results from other branches.

WHAT THIS PROGRAM DOES:
    1. Starts Policy and Claims branches in parallel.
    2. Policy branch successfully retrieves policy information.
    3. Claims branch simulates a service failure.
    4. Each branch handles its own exception.
    5. A reducer collects errors from parallel branches.
    6. The final node produces a PARTIAL SUCCESS response.

KEY CONCEPTS:
    - Parallel execution
    - Subgraph composition
    - try/except exception handling
    - Structured branch outcomes
    - Annotated[list[str], operator.add]
    - Partial result aggregation
    - Graceful degradation

EXPECTED FLOW:
    START
      |
      +---- Policy Branch (SUCCESS)
      |
      +---- Claims Branch (FAILED)
      |
      v
    Final Aggregation
      |
      v
    PARTIAL SUCCESS

IMPORTANT:
    A failure in one branch should not erase the successful
    result from another branch.

    This example catches exceptions inside each branch.
"""

import operator

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. DEFINE PARENT STATE
# ============================================================

class ParentState(TypedDict):

    customer_id: str

    policy_result: dict

    claims_result: dict

    # Multiple parallel branches can update this shared field.
    # operator.add combines their list updates.
    errors: Annotated[list[str], operator.add]

    final_response: str


# ============================================================
# 2. POLICY SUBGRAPH NODE
# ============================================================

def retrieve_policy(state: ParentState):

    print("Policy Subgraph: retrieving policy information...")

    try:

        # Simulated successful policy retrieval.
        policy_data = {
            "policy_status": "ACTIVE",
            "expiry_date": "2026-12-31"
        }

        return {
            "policy_result": {
                "status": "SUCCESS",
                "data": policy_data,
                "error": None
            },
            "errors": []
        }

    except Exception as error:

        return {
            "policy_result": {
                "status": "FAILED",
                "data": None,
                "error": str(error)
            },
            "errors": [f"Policy error: {error}"]
        }


# ============================================================
# 3. CLAIMS SUBGRAPH NODE
# ============================================================

def retrieve_claims(state: ParentState):

    print("Claims Subgraph: retrieving claim information...")

    try:

        # Simulate an external claims service failure.
        # raise ConnectionError(
        #     "Claims service is temporarily unavailable."
        # )

        # This code is not reached in this simulation.
        claims_data = {
            "claim_id": "CLM001",
            "status": "UNDER_REVIEW",
            "amount": 5000.00
        }

        return {
            "claims_result": {
                "status": "SUCCESS",
                "data": claims_data,
                "error": None
            },
            "errors": []
        }

    except Exception as error:

        print(f"Claims Subgraph Error: {error}")

        return {
            "claims_result": {
                "status": "FAILED",
                "data": None,
                "error": str(error)
            },
            "errors": [f"Claims error: {error}"]
        }


# ============================================================
# 4. FINAL AGGREGATION NODE
# ============================================================

def build_final_response(state: ParentState):

    policy = state["policy_result"]
    claims = state["claims_result"]

    errors = state["errors"]

    # Determine overall workflow status.
    if policy["status"] == "SUCCESS" and claims["status"] == "SUCCESS":

        overall_status = "SUCCESS"

    elif policy["status"] == "FAILED" and claims["status"] == "FAILED":

        overall_status = "FAILED"

    else:

        overall_status = "PARTIAL SUCCESS"

    response = []

    response.append(f"Customer: {state['customer_id']}")
    response.append(f"Overall Status: {overall_status}")

    # Preserve successful policy information.
    if policy["status"] == "SUCCESS":

        response.append(
            f"Policy: {policy['data']['policy_status']}"
        )

        response.append(
            f"Policy Expiry: {policy['data']['expiry_date']}"
        )

    else:

        response.append("Policy: Information unavailable")

    # Preserve successful claims information.
    if claims["status"] == "SUCCESS":

        response.append(
            f"Claim: {claims['data']['claim_id']}"
        )

        response.append(
            f"Claim Status: {claims['data']['status']}"
        )

    else:

        response.append("Claims: Information unavailable")

    # Include errors for transparency.
    if errors:

        response.append("Errors:")

        for error in sorted(errors):
            response.append(f"- {error}")

    return {
        "final_response": "\n".join(response)
    }


# ============================================================
# 5. BUILD PARENT GRAPH
# ============================================================

builder = StateGraph(ParentState)

builder.add_node("policy_subgraph", retrieve_policy)

builder.add_node("claims_subgraph", retrieve_claims)

builder.add_node("final_aggregation", build_final_response)


# ============================================================
# 6. DEFINE PARALLEL EXECUTION
# ============================================================

builder.add_edge(START, "policy_subgraph")

builder.add_edge(START, "claims_subgraph")


# Both branches must complete before final aggregation.
builder.add_edge("policy_subgraph", "final_aggregation")

builder.add_edge("claims_subgraph", "final_aggregation")

builder.add_edge("final_aggregation", END)


# ============================================================
# 7. COMPILE GRAPH
# ============================================================

graph = builder.compile()


# ============================================================
# 8. EXECUTE WORKFLOW
# ============================================================

if __name__ == "__main__":

    initial_state = {
        "customer_id": "CUST001",
        "policy_result": {},
        "claims_result": {},
        "errors": [],
        "final_response": ""
    }

    print("=" * 65)
    print("LESSON 71: PARALLEL SUBGRAPHS WITH ERROR HANDLING")
    print("=" * 65)

    result = graph.invoke(initial_state)

    print("\nFINAL AGGREGATED RESPONSE")
    print("-" * 65)

    print(result["final_response"])

    print("-" * 65)

    print("\nBRANCH EXECUTION SUMMARY")
    print("-" * 65)

    print("Policy Status :", result["policy_result"]["status"])

    print("Claims Status :", result["claims_result"]["status"])

    print("Total Errors  :", len(result["errors"]))

    print("=" * 65)
