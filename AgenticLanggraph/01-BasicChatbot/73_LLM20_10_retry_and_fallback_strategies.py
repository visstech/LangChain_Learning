
"""
=================================================================
LESSON 73: RETRY AND FALLBACK STRATEGIES
=================================================================

PURPOSE:
Demonstrate how to combine LangGraph RetryPolicy with a fallback
strategy in a parallel parent workflow.

SCENARIO:
1. Policy API succeeds.
2. Primary Claims API fails three times.
3. LangGraph RetryPolicy retries the primary Claims node.
4. A parent wrapper catches the exhausted exception.
5. The wrapper activates the fallback Claims API.
6. Final aggregation combines Policy and Claims results.

KEY CONCEPTS:
- Nested LangGraph subgraphs
- RetryPolicy
- Exception handling across graph boundaries
- Fallback execution
- Parallel branches and aggregation

EXPECTED FLOW:
Parent Graph
    |-- Policy Branch
    |
    |-- Claims Wrapper
          |-- Primary Claims Subgraph
          |      |-- Attempt 1: FAILED
          |      |-- Attempt 2: FAILED
          |      |-- Attempt 3: FAILED
          |
          |-- Catch ConnectionError
          |-- Execute Fallback Claims API

Final Aggregation
=================================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy


# ================================================================
# 1. EXECUTION COUNTERS
# ================================================================

primary_attempt_count = 0
fallback_attempt_count = 0


# ================================================================
# 2. PARENT GRAPH STATE
# ================================================================

class ParentState(TypedDict):
    customer_id: str
    policy_result: dict
    claims_result: dict
    final_response: str


# ================================================================
# 3. PRIMARY CLAIMS SUBGRAPH STATE
# ================================================================

class ClaimsState(TypedDict):
    customer_id: str
    claims_result: dict


# ================================================================
# 4. POLICY API NODE
# ================================================================

def retrieve_policy(state: ParentState):

    print("Policy API: retrieving policy information...")

    policy_result = {
        "status": "SUCCESS",
        "policy_status": "ACTIVE",
        "expiry_date": "2026-12-31"
    }

    print("Policy API succeeded.")

    return {
        "policy_result": policy_result
    }


# ================================================================
# 5. PRIMARY CLAIMS API NODE
# ================================================================

def retrieve_primary_claims(state: ClaimsState):

    global primary_attempt_count

    primary_attempt_count += 1

    print(
        f"Primary Claims API: attempt "
        f"{primary_attempt_count}..."
    )

    # Simulate primary Claims API failure.
    # LangGraph RetryPolicy will retry this node.

    raise ConnectionError(
        "Primary Claims API is unavailable."
    )


# ================================================================
# 6. BUILD PRIMARY CLAIMS SUBGRAPH
# ================================================================

claims_builder = StateGraph(ClaimsState)

claims_builder.add_node(
    "primary_claims",
    retrieve_primary_claims,
    retry_policy=RetryPolicy(
        max_attempts=3,
        initial_interval=0.5,
        backoff_factor=2.0,
        max_interval=2.0,
        jitter=False,
        retry_on=(ConnectionError,)
    )
)

claims_builder.add_edge(
    START,
    "primary_claims"
)

claims_builder.add_edge(
    "primary_claims",
    END
)

primary_claims_graph = claims_builder.compile()


# ================================================================
# 7. FALLBACK CLAIMS API NODE
# ================================================================

def retrieve_fallback_claims(state: ParentState):

    global fallback_attempt_count

    fallback_attempt_count += 1

    print("Fallback Claims API: retrieving claim information...")

    claims_result = {
        "status": "SUCCESS",
        "source": "FALLBACK_API",
        "claim_id": "CLM001",
        "claim_status": "UNDER_REVIEW",
        "amount": 5000.00
    }

    print("Fallback Claims API succeeded.")

    return {
        "claims_result": claims_result
    }


# ================================================================
# 8. CLAIMS WRAPPER WITH FALLBACK
# ================================================================

def retrieve_claims_with_fallback(state: ParentState):

    print(
        "Claims workflow: invoking primary Claims subgraph..."
    )

    try:

        # Invoke the nested primary Claims subgraph.
        # RetryPolicy executes inside this subgraph.

        primary_result = primary_claims_graph.invoke({
            "customer_id": state["customer_id"],
            "claims_result": {}
        })

        # This section runs if the primary API succeeds.

        return {
            "claims_result": primary_result["claims_result"]
        }

    except ConnectionError as error:

        # The primary subgraph exhausted its retries.
        # The wrapper catches the propagated exception.

        print("\nPrimary Claims API retries exhausted.")
        print(f"Primary error: {error}")

        print("Activating fallback Claims API...")

        return retrieve_fallback_claims(state)


# ================================================================
# 9. FINAL AGGREGATION NODE
# ================================================================

def final_aggregation(state: ParentState):

    policy = state["policy_result"]
    claims = state["claims_result"]

    response = f"""
=================================================================
FINAL AGGREGATED RESPONSE
=================================================================

Customer              : {state['customer_id']}
Overall Status        : SUCCESS

Policy Status         : {policy['policy_status']}
Policy Expiry         : {policy['expiry_date']}

Claim ID              : {claims['claim_id']}
Claim Status          : {claims['claim_status']}
Claim Amount          : RM {claims['amount']:.2f}

Claims Data Source    : {claims['source']}

=================================================================
"""

    return {
        "final_response": response
    }


# ================================================================
# 10. BUILD PARENT GRAPH
# ================================================================

builder = StateGraph(ParentState)

builder.add_node(
    "retrieve_policy",
    retrieve_policy
)

builder.add_node(
    "retrieve_claims_with_fallback",
    retrieve_claims_with_fallback
)

builder.add_node(
    "final_aggregation",
    final_aggregation
)


# Start both branches in parallel.

builder.add_edge(
    START,
    "retrieve_policy"
)

builder.add_edge(
    START,
    "retrieve_claims_with_fallback"
)


# Both branches must complete before final aggregation.

builder.add_edge(
    "retrieve_policy",
    "final_aggregation"
)

builder.add_edge(
    "retrieve_claims_with_fallback",
    "final_aggregation"
)

builder.add_edge(
    "final_aggregation",
    END
)


# ================================================================
# 11. COMPILE AND EXECUTE
# ================================================================

graph = builder.compile()

initial_state = {
    "customer_id": "CUST001",
    "policy_result": {},
    "claims_result": {},
    "final_response": ""
}

print("=" * 65)
print("LESSON 73: RETRY AND FALLBACK STRATEGIES")
print("=" * 65)

result = graph.invoke(initial_state)

print(result["final_response"])


# ================================================================
# 12. EXECUTION SUMMARY
# ================================================================

print("EXECUTION SUMMARY")
print("-" * 65)

print(f"Primary API Attempts : {primary_attempt_count}")
print(f"Fallback API Calls   : {fallback_attempt_count}")

print("\nLesson 73 execution completed.")
