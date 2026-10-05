"""
====================================================================
65 - LANGGRAPH SUBGRAPH WITH DIFFERENT STATE SCHEMAS
====================================================================

WHAT THIS PROGRAM DOES
----------------------
This program demonstrates how a Parent Graph can call a Subgraph
when the Parent State and Child State have completely different
schemas.

Unlike Lesson 64, where the parent and child both worked mainly
with a simple "message" field, this lesson demonstrates explicit
state mapping.

REAL-WORLD SCENARIO
-------------------
Imagine an Insurance AI Agent.

The Parent Graph receives:

    customer_id
    claim_id
    user_message

The Claims Subgraph needs different information:

    claim_id
    claim_amount
    claim_status
    decision

The parent therefore maps its state into the child's state.

After the child graph finishes, the parent maps the child's result
back into the parent's state.

GRAPH FLOW
----------
                PARENT GRAPH
                     |
                     v
              Prepare Request
                     |
                     v
          Map Parent -> Child State
                     |
                     v
              CLAIMS SUBGRAPH
             +---------------+
             | Claim Lookup  |
             |      |        |
             |      v        |
             | Decision      |
             +---------------+
                     |
                     v
          Map Child -> Parent State
                     |
                     v
             Final Response

KEY CONCEPTS
------------
1. Parent Graph
2. Subgraph
3. Different State Schemas
4. Explicit State Mapping
5. Parent -> Child Mapping
6. Child -> Parent Mapping
7. Modular Graph Design

IMPORTANT
---------
The ParentState and ClaimsState are intentionally different.

ParentState:
    customer_id
    claim_id
    user_message
    final_response

ClaimsState:
    claim_id
    claim_amount
    claim_status
    decision

The parent controls how information is passed into and received
from the subgraph.

EXPECTED FLOW
-------------
1. Parent receives customer and claim information.
2. Parent calls the Claims Subgraph.
3. Parent maps its claim_id into ClaimsState.
4. Claims Subgraph looks up the claim.
5. Claims Subgraph determines a decision.
6. Child result is returned to the parent.
7. Parent maps the child result into final_response.
8. Parent Graph completes.

====================================================================
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ==================================================================
# STEP 1 - DEFINE THE CHILD / SUBGRAPH STATE
# ==================================================================

class ClaimsState(TypedDict):
    """
    State used ONLY inside the Claims Subgraph.

    Notice that this schema is different from ParentState.
    """

    claim_id: str
    claim_amount: float
    claim_status: str
    decision: str


# ==================================================================
# STEP 2 - CLAIM LOOKUP NODE
# ==================================================================

def claim_lookup(state: ClaimsState):
    """
    Simulates retrieving claim information.

    In a real application this could call:
        - PostgreSQL
        - REST API
        - Claims Service
        - Insurance database
    """

    print("Claims Subgraph: looking up claim...")

    claim_status_map = {
        "CLM001": "UNDER_REVIEW",
        "CLM002": "APPROVED",
    }

    claim_amount_map = {
        "CLM001": 5000.0,
        "CLM002": 2500.0,
    }

    claim_id = state["claim_id"]

    return {
        "claim_status": claim_status_map.get(
            claim_id,
            "NOT_FOUND"
        ),
        "claim_amount": claim_amount_map.get(
            claim_id,
            0.0
        ),
    }


# ==================================================================
# STEP 3 - CLAIM DECISION NODE
# ==================================================================

def claim_decision(state: ClaimsState):
    """
    Determines what should happen based on claim status.
    """

    print("Claims Subgraph: making decision...")

    if state["claim_status"] == "UNDER_REVIEW":
        decision = "WAIT"

    elif state["claim_status"] == "APPROVED":
        decision = "PROCEED"

    else:
        decision = "NO_ACTION"

    return {
        "decision": decision
    }


# ==================================================================
# STEP 4 - BUILD THE CLAIMS SUBGRAPH
# ==================================================================

claims_builder = StateGraph(ClaimsState)

claims_builder.add_node(
    "claim_lookup",
    claim_lookup
)

claims_builder.add_node(
    "claim_decision",
    claim_decision
)

claims_builder.add_edge(
    START,
    "claim_lookup"
)

claims_builder.add_edge(
    "claim_lookup",
    "claim_decision"
)

claims_builder.add_edge(
    "claim_decision",
    END
)

claims_graph = claims_builder.compile()


# ==================================================================
# STEP 5 - DEFINE THE PARENT STATE
# ==================================================================

class ParentState(TypedDict):
    """
    State used by the Parent Graph.

    Notice that this schema is completely different from
    ClaimsState.
    """

    customer_id: str
    claim_id: str
    user_message: str
    final_response: str


# ==================================================================
# STEP 6 - PARENT NODE
# ==================================================================

def parent_prepare(state: ParentState):
    """
    Parent prepares the request before calling the subgraph.
    """

    print("Parent Graph: preparing request...")

    return {}


# ==================================================================
# STEP 7 - PARENT -> CHILD STATE MAPPING
# ==================================================================

def call_claims_subgraph(state: ParentState):
    """
    Explicitly maps ParentState into ClaimsState.

    Parent has:

        customer_id
        claim_id
        user_message
        final_response

    Child needs:

        claim_id
        claim_amount
        claim_status
        decision
    """

    print("Parent Graph: mapping Parent State -> Claims State...")
    print("Parent Graph: calling Claims Subgraph...")

    child_result = claims_graph.invoke(
        {
            "claim_id": state["claim_id"],
            "claim_amount": 0.0,
            "claim_status": "UNKNOWN",
            "decision": "UNKNOWN",
        }
    )

    # --------------------------------------------------------------
    # Child -> Parent mapping
    # --------------------------------------------------------------

    return {
        "final_response": (
            f"Customer {state['customer_id']} | "
            f"Claim {state['claim_id']} | "
            f"Amount: RM{child_result['claim_amount']:.2f} | "
            f"Status: {child_result['claim_status']} | "
            f"Decision: {child_result['decision']}"
        )
    }


# ==================================================================
# STEP 8 - BUILD THE PARENT GRAPH
# ==================================================================

parent_builder = StateGraph(ParentState)

parent_builder.add_node(
    "parent_prepare",
    parent_prepare
)

parent_builder.add_node(
    "call_claims_subgraph",
    call_claims_subgraph
)

parent_builder.add_edge(
    START,
    "parent_prepare"
)

parent_builder.add_edge(
    "parent_prepare",
    "call_claims_subgraph"
)

parent_builder.add_edge(
    "call_claims_subgraph",
    END
)

parent_graph = parent_builder.compile()


# ==================================================================
# STEP 9 - RUN THE PARENT GRAPH
# ==================================================================

print()
print("=" * 60)
print("65 - SUBGRAPH WITH DIFFERENT STATE SCHEMAS")
print("=" * 60)

result = parent_graph.invoke(
    {
        "customer_id": "CUST001",
        "claim_id": "CLM001",
        "user_message": "What is the status of my claim?",
        "final_response": "",
    }
)


# ==================================================================
# STEP 10 - DISPLAY FINAL RESULT
# ==================================================================

print()
print("=" * 60)
print("FINAL RESULT")
print("=" * 60)

print(result)

print()
print("=" * 60)
print("GRAPH COMPLETED")
print("=" * 60)