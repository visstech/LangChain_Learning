"""
=================================================================
LESSON 72: PARALLEL SUBGRAPHS WITH RETRY POLICY
=================================================================

PURPOSE
-------
Learn how LangGraph automatically retries a failed node using
RetryPolicy.

SCENARIO
--------
1. Policy branch retrieves policy information successfully.
2. Claims branch calls a simulated Claims API.
3. Claims API fails on attempts 1 and 2.
4. Claims API succeeds on attempt 3.
5. LangGraph automatically retries the Claims node.
6. Final aggregation combines both successful results.

KEY CONCEPTS
------------
- RetryPolicy
- max_attempts
- initial_interval
- backoff_factor
- max_interval
- retry_on
- Automatic node retries
- Parallel branch execution

IMPORTANT
---------
Do not catch the simulated ConnectionError inside the Claims node.
The exception must reach LangGraph so RetryPolicy can handle it.

The global attempt counter is only a simple simulation mechanism.
In production, retry attempts would be driven by real service calls.

EXPECTED FLOW
-------------
Policy branch  --------------------------> SUCCESS
Claims branch --> Attempt 1 --> FAILED
               --> Attempt 2 --> FAILED
               --> Attempt 3 --> SUCCESS

Final aggregation --> SUCCESS
=================================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy


# ---------------------------------------------------------------
# STEP 1: Simulated Claims API attempt counter
# ---------------------------------------------------------------

claims_attempt_count = 0


# ---------------------------------------------------------------
# STEP 2: Define the parent graph state
# ---------------------------------------------------------------

class ParentState(TypedDict):
    customer_id: str
    policy_result: dict
    claims_result: dict
    final_response: str


# ---------------------------------------------------------------
# STEP 3: Policy branch
# ---------------------------------------------------------------

def retrieve_policy(state: ParentState):

    print("Policy Subgraph: retrieving policy information...")

    policy_result = {
        "status": "SUCCESS",
        "policy_status": "ACTIVE",
        "expiry_date": "2026-12-31"
    }

    return {
        "policy_result": policy_result
    }


# ---------------------------------------------------------------
# STEP 4: Claims branch with simulated temporary failures
# ---------------------------------------------------------------

def retrieve_claims(state: ParentState):

    global claims_attempt_count

    claims_attempt_count += 1

    print(
        f"Claims Subgraph: API attempt "
        f"{claims_attempt_count}..."
    )

    # Simulate temporary service failures on attempts 1 and 2.
    if claims_attempt_count < 3:

        print(
            f"Claims API failed on attempt "
            f"{claims_attempt_count}."
        )

        raise ConnectionError(
            "Claims service is temporarily unavailable."
        )

    # Attempt 3 succeeds.
    print("Claims API succeeded!")

    claims_result = {
        "status": "SUCCESS",
        "claim_id": "CLM001",
        "claim_status": "UNDER_REVIEW",
        "amount": 5000.00
    }

    return {
        "claims_result": claims_result
    }


# ---------------------------------------------------------------
# STEP 5: Final aggregation
# ---------------------------------------------------------------

def final_aggregation(state: ParentState):

    policy = state["policy_result"]
    claims = state["claims_result"]

    final_response = (
        f"Customer: {state['customer_id']}\n"
        f"Overall Status: SUCCESS\n"
        f"Policy: {policy['policy_status']}\n"
        f"Policy Expiry: {policy['expiry_date']}\n"
        f"Claim: {claims['claim_id']}\n"
        f"Claim Status: {claims['claim_status']}\n"
        f"Claim Amount: RM{claims['amount']:.2f}\n"
        f"Claims API Attempts: {claims_attempt_count}"
    )

    return {
        "final_response": final_response
    }


# ---------------------------------------------------------------
# STEP 6: Build the parallel graph with RetryPolicy
# ---------------------------------------------------------------

builder = StateGraph(ParentState)

# Policy branch does not require retry configuration.
builder.add_node(
    "retrieve_policy",
    retrieve_policy
)

# Claims branch automatically retries ConnectionError.
builder.add_node(
    "retrieve_claims",
    retrieve_claims,
    retry_policy=RetryPolicy(
        max_attempts=3,
        initial_interval=0.5,
        backoff_factor=2.0,
        max_interval=2.0,
        jitter=False,
        retry_on=(ConnectionError,)
    )
)

builder.add_node(
    "final_aggregation",
    final_aggregation
)


# ---------------------------------------------------------------
# STEP 7: Define parallel execution and fan-in
# ---------------------------------------------------------------

builder.add_edge(START, "retrieve_policy")
builder.add_edge(START, "retrieve_claims")

builder.add_edge(
    "retrieve_policy",
    "final_aggregation"
)

builder.add_edge(
    "retrieve_claims",
    "final_aggregation"
)

builder.add_edge("final_aggregation", END)


# ---------------------------------------------------------------
# STEP 8: Compile and execute
# ---------------------------------------------------------------

graph = builder.compile()


if __name__ == "__main__":

    # Reset the simulation counter for each program run.
    claims_attempt_count = 0

    initial_state = {
        "customer_id": "CUST001",
        "policy_result": {},
        "claims_result": {},
        "final_response": ""
    }

    print("=" * 65)
    print("LESSON 72: PARALLEL SUBGRAPHS WITH RETRY POLICY")
    print("=" * 65)

    result = graph.invoke(initial_state)

    print("\nFINAL AGGREGATED RESPONSE")
    print("-" * 65)
    print(result["final_response"])
    print("-" * 65)

    print("\nRETRY EXECUTION SUMMARY")
    print("-" * 65)
    print(f"Claims API Attempts : {claims_attempt_count}")
    print("Policy Status       : SUCCESS")
    print("Claims Status       : SUCCESS")
    print("Overall Status      : SUCCESS")
    print("=" * 65)