"""
====================================================================
66 - LANGGRAPH REUSABLE SUBGRAPH AS A MODULAR WORKFLOW
====================================================================

WHAT THIS PROGRAM DOES
----------------------
This program demonstrates how a compiled LangGraph subgraph can be
created once and reused by multiple parent workflows.

We will build a reusable "Claims Subgraph".

Two different workflows will use the SAME subgraph:

    1. Claim Status Workflow
    2. Claim Review Workflow

This demonstrates modular and reusable LangGraph architecture.

REAL-WORLD SCENARIO
-------------------
Imagine an Insurance AI system.

Several different workflows may need to retrieve claim information.

For example:

    Customer asks:
        "What is the status of my claim?"

    Internal reviewer asks:
        "Can I review this claim?"

Both workflows need claim information.

Instead of implementing claim lookup separately in both workflows,
we create one reusable Claims Subgraph.

ARCHITECTURE
------------

                    REUSABLE
                CLAIMS SUBGRAPH
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
      STATUS WORKFLOW    REVIEW WORKFLOW
             │                │
             ▼                ▼
       Status Result      Review Result


KEY CONCEPTS
------------
1. Reusable subgraph
2. Compiled graph
3. Modular architecture
4. Separation of responsibilities
5. Avoiding duplicated logic
6. Multiple workflows using one subgraph

IMPORTANT
---------
The Claims Subgraph is compiled only ONCE:

    claims_graph = claims_builder.compile()

Then both workflows call:

    claims_graph.invoke(...)

This means the claim lookup logic is implemented only once.

EXPECTED FLOW
-------------
1. Build Claims Subgraph.
2. Compile Claims Subgraph.
3. Build Status Workflow.
4. Status Workflow calls Claims Subgraph.
5. Build Review Workflow.
6. Review Workflow calls the SAME Claims Subgraph.
7. Display results from both workflows.

====================================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ==================================================================
# STEP 1 - DEFINE CLAIMS SUBGRAPH STATE
# ==================================================================

class ClaimsState(TypedDict):
    """
    State used by the reusable Claims Subgraph.
    """

    claim_id: str
    claim_status: str
    claim_amount: float


# ==================================================================
# STEP 2 - CLAIM LOOKUP NODE
# ==================================================================

def claim_lookup(state: ClaimsState):
    """
    Simulates retrieving claim information.

    In a real Insurance AI Agent this could call:

        - PostgreSQL
        - Claims API
        - Insurance database
        - ClaimService
    """

    print(
        f"Claims Subgraph: looking up {state['claim_id']}..."
    )

    claim_data = {
        "CLM001": {
            "status": "UNDER_REVIEW",
            "amount": 5000.0,
        },
        "CLM002": {
            "status": "APPROVED",
            "amount": 2500.0,
        },
    }

    claim = claim_data.get(state["claim_id"])

    if claim is None:
        return {
            "claim_status": "NOT_FOUND",
            "claim_amount": 0.0,
        }

    return {
        "claim_status": claim["status"],
        "claim_amount": claim["amount"],
    }


# ==================================================================
# STEP 3 - BUILD THE REUSABLE CLAIMS SUBGRAPH
# ==================================================================

claims_builder = StateGraph(ClaimsState)

claims_builder.add_node(
    "claim_lookup",
    claim_lookup
)

claims_builder.add_edge(
    START,
    "claim_lookup"
)

claims_builder.add_edge(
    "claim_lookup",
    END
)


# ==================================================================
# STEP 4 - COMPILE THE SUBGRAPH ONCE
# ==================================================================

claims_graph = claims_builder.compile()


# ==================================================================
# STATUS WORKFLOW
# ==================================================================

# ------------------------------------------------------------------
# STEP 5 - STATUS WORKFLOW STATE
# ------------------------------------------------------------------

class StatusWorkflowState(TypedDict):
    claim_id: str
    response: str


# ------------------------------------------------------------------
# STEP 6 - STATUS WORKFLOW NODE
# ------------------------------------------------------------------

def check_claim_status(state: StatusWorkflowState):
    """
    STATUS WORKFLOW

    Calls the reusable Claims Subgraph.
    """

    print()
    print(
        "Status Workflow: calling reusable Claims Subgraph..."
    )

    result = claims_graph.invoke(
        {
            "claim_id": state["claim_id"],
            "claim_status": "UNKNOWN",
            "claim_amount": 0.0,
        }
    )

    return {
        "response": (
            f"Claim {state['claim_id']} | "
            f"Status: {result['claim_status']} | "
            f"Amount: RM{result['claim_amount']:.2f}"
        )
    }


# ------------------------------------------------------------------
# STEP 7 - BUILD STATUS WORKFLOW
# ------------------------------------------------------------------

status_builder = StateGraph(StatusWorkflowState)

status_builder.add_node(
    "check_claim_status",
    check_claim_status
)

status_builder.add_edge(
    START,
    "check_claim_status"
)

status_builder.add_edge(
    "check_claim_status",
    END
)

status_graph = status_builder.compile()


# ==================================================================
# REVIEW WORKFLOW
# ==================================================================

# ------------------------------------------------------------------
# STEP 8 - REVIEW WORKFLOW STATE
# ------------------------------------------------------------------

class ReviewWorkflowState(TypedDict):
    claim_id: str
    review_result: str


# ------------------------------------------------------------------
# STEP 9 - REVIEW WORKFLOW NODE
# ------------------------------------------------------------------

def review_claim(state: ReviewWorkflowState):
    """
    REVIEW WORKFLOW

    This is a different workflow.

    However, it reuses the SAME Claims Subgraph.
    """

    print()
    print(
        "Review Workflow: calling reusable Claims Subgraph..."
    )

    result = claims_graph.invoke(
        {
            "claim_id": state["claim_id"],
            "claim_status": "UNKNOWN",
            "claim_amount": 0.0,
        }
    )

    if result["claim_status"] == "UNDER_REVIEW":

        review = "Manual review required"

    elif result["claim_status"] == "APPROVED":

        review = "Claim already approved"

    elif result["claim_status"] == "NOT_FOUND":

        review = "Claim could not be found"

    else:

        review = "Review status unknown"

    return {
        "review_result": (
            f"Claim {state['claim_id']} | "
            f"Status: {result['claim_status']} | "
            f"Review: {review}"
        )
    }


# ------------------------------------------------------------------
# STEP 10 - BUILD REVIEW WORKFLOW
# ------------------------------------------------------------------

review_builder = StateGraph(ReviewWorkflowState)

review_builder.add_node(
    "review_claim",
    review_claim
)

review_builder.add_edge(
    START,
    "review_claim"
)

review_builder.add_edge(
    "review_claim",
    END
)

review_graph = review_builder.compile()


# ==================================================================
# RUN THE PROGRAM
# ==================================================================

print()
print("=" * 60)
print("66 - REUSABLE SUBGRAPH AS MODULAR WORKFLOW")
print("=" * 60)


# ==================================================================
# RUN WORKFLOW A
# ==================================================================

print()
print("-" * 60)
print("WORKFLOW A - CLAIM STATUS")
print("-" * 60)

status_result = status_graph.invoke(
    {
        "claim_id": "CLM001",
        "response": "",
    }
)

print()
print("Status Result:")
print(status_result)


# ==================================================================
# RUN WORKFLOW B
# ==================================================================

print()
print("-" * 60)
print("WORKFLOW B - CLAIM REVIEW")
print("-" * 60)

review_result = review_graph.invoke(
    {
        "claim_id": "CLM001",
        "review_result": "",
    }
)

print()
print("Review Result:")
print(review_result)


# ==================================================================
# COMPLETION
# ==================================================================

print()
print("=" * 60)
print("REUSABLE SUBGRAPH DEMONSTRATION COMPLETED")
print("=" * 60)