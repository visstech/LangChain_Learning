"""
=================================================================
LESSON 74: TIMEOUT HANDLING AND GRACEFUL DEGRADATION
=================================================================

PURPOSE:
Handle slow API operations in parallel LangGraph workflows
without failing the entire workflow.

WHAT THIS PROGRAM DOES:
1. Executes Policy and Analytics services in parallel.
2. Policy service responds successfully.
3. Analytics service exceeds its configured timeout.
4. Captures TimeoutError.
5. Continues with available information.
6. Aggregates results using LangGraph.

KEY CONCEPTS:
- asyncio
- async / await
- asyncio.wait_for()
- TimeoutError
- Graceful degradation
- Partial success
- Parallel graph execution

EXPECTED FLOW:
START
  |
  +---- Policy Service -------- SUCCESS
  |
  +---- Analytics Service ----- TIMEOUT
  |
  v
Final Aggregation
  |
  v
PARTIAL SUCCESS
=================================================================
"""

import asyncio

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

# ==============================================================
# STEP 1: DEFINE WORKFLOW STATE
# ==============================================================

class WorkflowState(TypedDict):

    customer_id: str

    policy_result: dict

    analytics_result: dict

    final_response: str

    overall_status: str

# ==============================================================
# STEP 2: SIMULATE EXTERNAL SERVICES
# ==============================================================

async def policy_api(customer_id: str):

    print("Policy API: Processing request...")

    await asyncio.sleep(0.2)

    return {
        "status": "SUCCESS",
        "policy_number": "POL1001",
        "policy_status": "ACTIVE"
    }


async def analytics_api(customer_id: str):

    print("Analytics API: Processing request...")

    # # Simulate a slow external service.
    # Unlike time.sleep(), asyncio.sleep() allows other asynchronous tasks to progress while waiting.
    await asyncio.sleep(2.0)

    return {
        "status": "SUCCESS",
        "risk_score": 25
    }

# ==============================================================
# STEP 3: POLICY SERVICE NODE
# ==============================================================

async def retrieve_policy(state: WorkflowState):

    customer_id = state["customer_id"]

    result = await policy_api(customer_id)

    print("Policy API: Completed successfully.")

    return {
        "policy_result": result
    }    

# ==============================================================
# STEP 4: ANALYTICS SERVICE WITH TIMEOUT
# ==============================================================

async def retrieve_analytics(state: WorkflowState):

    customer_id = state["customer_id"]

    print("Analytics API: Starting request...")

    try:

        # Allow maximum 0.5 seconds for the API response.
        result = await asyncio.wait_for(
            analytics_api(customer_id),
            timeout=3.0
        )

        print("Analytics API: Completed successfully.")

        return {
            "analytics_result": result
        }

    except TimeoutError:

        print("Analytics API: TIMEOUT OCCURRED.")

        # Graceful degradation:
        # Return a controlled result instead of failing the graph.

        return {
            "analytics_result": {
                "status": "TIMEOUT",
                "risk_score": None,
                "message": "Analytics service unavailable within timeout."
            }
        }

# ==============================================================
# STEP 5: FINAL AGGREGATION
# ==============================================================

def final_aggregation(state: WorkflowState):

    policy = state["policy_result"]

    analytics = state["analytics_result"]

    if (
        policy["status"] == "SUCCESS"
        and analytics["status"] == "SUCCESS"
    ):
        overall_status = "SUCCESS"

    else:
        overall_status = "PARTIAL SUCCESS"

    response = f"""
CUSTOMER: {state['customer_id']}

POLICY INFORMATION:
Policy Number: {policy.get('policy_number')}
Policy Status: {policy.get('policy_status')}

ANALYTICS INFORMATION:
Analytics Status: {analytics['status']}
Risk Score: {analytics.get('risk_score')}

OVERALL STATUS: {overall_status}
"""

    print("\nFinal aggregation completed.")

    return {
        "final_response": response,
        "overall_status": overall_status
    }

# ==============================================================
# STEP 6: BUILD LANGGRAPH WORKFLOW
# ==============================================================

builder = StateGraph(WorkflowState)

# Register nodes.
builder.add_node(
    "retrieve_policy",
    retrieve_policy
)

builder.add_node(
    "retrieve_analytics",
    retrieve_analytics
)

builder.add_node(
    "final_aggregation",
    final_aggregation
)

# Start both services in parallel.
builder.add_edge(
    START,
    "retrieve_policy"
)

builder.add_edge(
    START,
    "retrieve_analytics"
)

# Wait for both parallel branches.
builder.add_edge(
    [
        "retrieve_policy",
        "retrieve_analytics"
    ],
    "final_aggregation"
)

builder.add_edge(
    "final_aggregation",
    END
)

graph = builder.compile()

# ==============================================================
# STEP 7: EXECUTE WORKFLOW
# ==============================================================

async def main():

    initial_state = {
        "customer_id": "CUST001",
        "policy_result": {},
        "analytics_result": {},
        "final_response": "",
        "overall_status": ""
    }

    print("=" * 65)
    print("LESSON 74: TIMEOUT AND GRACEFUL DEGRADATION")
    print("=" * 65)

    result = await graph.ainvoke(initial_state)
    
    assert result["policy_result"]["status"] == "SUCCESS"

    assert result["analytics_result"]["status"] == "SUCCESS"

    assert result["analytics_result"]["risk_score"] == 25

    assert result["overall_status"] == "SUCCESS"

    print("\nALL LESSON 74 VALIDATIONS PASSED.")

    print("\nFINAL RESPONSE")
    print("-" * 65)

    print(result["final_response"])

    print("OVERALL STATUS:", result["overall_status"])


if __name__ == "__main__":

    asyncio.run(main())