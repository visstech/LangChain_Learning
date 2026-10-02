"""
============================================================
20.9.8 - ERROR CLASSIFICATION + FALLBACK
============================================================

PURPOSE
-------
This program demonstrates how to classify different types
of errors and apply different recovery strategies.

We will handle three categories:

1. TRANSIENT
   Example:
       ConnectionError

   Action:
       Retry

2. BUSINESS
   Example:
       ValueError / Claim not found

   Action:
       Graceful fallback

3. SYSTEM
   Example:
       Unexpected system failure

   Action:
       Return a controlled FAILED result

KEY CONCEPTS
------------
- Send
- RetryPolicy
- Error classification
- Transient errors
- Business errors
- System errors
- Fallback
- Structured results
- Fan-out / Fan-in

EXPECTED FLOW
-------------

                    CLAIM
                      |
                      v
                Process Claim
                      |
                      v
                Error occurs
                      |
                      v
               Classify Error
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      TRANSIENT    BUSINESS     SYSTEM
          |           |           |
          v           v           v
        RETRY      FALLBACK      FAIL
          |           |           |
          +-----------+-----------+
                      |
                      v
                Final Results
============================================================
"""

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy

import operator


# ============================================================
# 1. GRAPH STATE
# ============================================================

class State(TypedDict):

    claims: list
    
    #Annotated[list, operator.add] = “This is a list, and keep adding new items to it.” 
    # operator.add([1, 2], [3, 4]) is effectively:[1, 2] + [3, 4] Result:[1, 2, 3, 4]
    
    '''Send()
            ↓
            Multiple parallel workers
            ↓
            Each worker returns a result
            ↓
            Annotated[list, operator.add]
            ↓
            LangGraph combines all results'''

    results: Annotated[
        list,
        operator.add
    ]


# ============================================================
# 2. CLAIM DATA
# ============================================================

claims_data = [

    {
        "claim_id": "CLM001",
        "behavior": "success"
    },

    {
        "claim_id": "CLM002",
        "behavior": "transient"
    },

    {
        "claim_id": "CLM003",
        "behavior": "business"
    },

    {
        "claim_id": "CLM004",
        "behavior": "system"
    },
]


# ============================================================
# 3. ATTEMPT TRACKING
# ============================================================

attempts = {}


# ============================================================
# 4. PREPARE CLAIMS
# ============================================================

def prepare_claims(state: State):

    print("\nPreparing claims...")

    return {
        "claims": claims_data
    }


# ============================================================
# 5. FAN-OUT USING SEND
# ============================================================

def dispatch_claims(state: State):

    print("\nDispatching claims using Send...")
    
    #Send(
    #DESTINATION,
    #DATA
    #)
    # means:Send claim_data → to process_claim.
        
    return [

        Send(
            "process_claim",#first parameter name of the LangGraph node that should receive this work
            {
                "claim_id": claim["claim_id"],#The second parameter is the input to process_claim
                "behavior": claim["behavior"],
            }
        )

        for claim in state["claims"]
    ]


# ============================================================
# 6. ERROR CLASSIFICATION
# ============================================================

def classify_error(error: Exception) -> str:

    """
    Classify an exception into a recovery category.

    ConnectionError
        -> TRANSIENT

    ValueError
        -> BUSINESS

    Everything else
        -> SYSTEM
    """

    if isinstance(
        error,
        ConnectionError
    ):

        return "TRANSIENT"


    if isinstance(
        error,
        ValueError
    ):

        return "BUSINESS"


    return "SYSTEM"


# ============================================================
# 7. PROCESS CLAIM
# ============================================================

def process_claim(state):

    claim_id = state["claim_id"]

    behavior = state["behavior"]


    # --------------------------------------------------------
    # Track attempts
    # --------------------------------------------------------

    attempts[claim_id] = (
        attempts.get(claim_id, 0) + 1
    )

    attempt = attempts[claim_id]


    print(
        f"\nProcessing {claim_id} "
        f"(attempt {attempt})"
    )


    # ========================================================
    # CASE 1 - SUCCESS
    # ========================================================

    if behavior == "success":

        print(
            f"{claim_id} processed successfully."
        )

        return {

            "results": [

                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": attempt
                }

            ]

        }


    # ========================================================
    # CASE 2 - TRANSIENT ERROR
    # ========================================================

    if behavior == "transient":

        if attempt == 1:

            print(
                f"{claim_id}: "
                f"temporary connection failure."
            )

            # IMPORTANT:
            #
            # We raise the exception.
            #
            # RetryPolicy will see it.

            raise ConnectionError(
                "Temporary database connection failure"
            )


        print(
            f"{claim_id} succeeded after retry."
        )

        return {

            "results": [

                {
                    "claim_id": claim_id,
                    "status": "SUCCESS",
                    "attempts": attempt
                }

            ]

        }


    # ========================================================
    # CASE 3 - BUSINESS ERROR
    # ========================================================

    if behavior == "business":

        try:

            print(
                f"{claim_id}: "
                f"claim does not exist."
            )

            raise ValueError(
                "Claim not found"
            )


        except ValueError as error:

            error_type = classify_error(
                error
            )

            print(
                f"{claim_id}: "
                f"error classified as "
                f"{error_type}"
            )


            # ------------------------------------------------
            # BUSINESS FALLBACK
            # ------------------------------------------------

            return {

                "results": [

                    {
                        "claim_id": claim_id,
                        "status": "NOT_FOUND",
                        "error_type": error_type,
                        "error": str(error),
                        "attempts": attempt
                    }

                ]

            }


    # ========================================================
    # CASE 4 - SYSTEM ERROR
    # ========================================================

    if behavior == "system":

        try:

            print(
                f"{claim_id}: "
                f"unexpected system error."
            )

            raise RuntimeError(
                "Unexpected internal processing failure"
            )


        except Exception as error:

            error_type = classify_error(
                error
            )

            print(
                f"{claim_id}: "
                f"error classified as "
                f"{error_type}"
            )


            # ------------------------------------------------
            # SYSTEM FAILURE RESULT
            # ------------------------------------------------

            return {

                "results": [

                    {
                        "claim_id": claim_id,
                        "status": "FAILED",
                        "error_type": error_type,
                        "error": str(error),
                        "attempts": attempt
                    }

                ]

            }


# ============================================================
# 8. RETRY POLICY
# ============================================================

def should_retry(
    error: Exception
) -> bool:

    """
    Only ConnectionError is retryable.
    """

    return isinstance(
        error,
        ConnectionError
    )


# ============================================================
# 9. BUILD GRAPH
# ============================================================

builder = StateGraph(State)


builder.add_node(
    "prepare_claims",
    prepare_claims
)


builder.add_node(

    "process_claim",

    process_claim,

    retry_policy=RetryPolicy(

        max_attempts=3,

        retry_on=should_retry

    )

)


# ============================================================
# 10. GRAPH EDGES
# ============================================================

builder.add_edge(
    START,
    "prepare_claims"
)


builder.add_conditional_edges(
    "prepare_claims",
    dispatch_claims
)


builder.add_edge(
    "process_claim",
    END
)


# ============================================================
# 11. COMPILE
# ============================================================

graph = builder.compile()


# ============================================================
# 12. INITIAL STATE
# ============================================================

initial_state = {

    "claims": [],

    "results": []

}


# ============================================================
# 13. RUN GRAPH
# ============================================================

print(
    "\n" + "=" * 60
)

print(
    "20.9.8 - ERROR CLASSIFICATION + FALLBACK"
)

print(
    "=" * 60
)


final_state = graph.invoke(
    initial_state
)


# ============================================================
# 14. FINAL REPORT
# ============================================================

print(
    "\n" + "=" * 60
)

print(
    "FINAL REPORT"
)

print(
    "=" * 60
)


for result in final_state["results"]:

    print(
        f"\n{result['claim_id']} "
        f"-> {result['status']}"
    )


    print(
        f"   Attempts    : "
        f"{result['attempts']}"
    )


    if "error_type" in result:

        print(
            f"   Error Type  : "
            f"{result['error_type']}"
        )


    if "error" in result:

        print(
            f"   Error       : "
            f"{result['error']}"
        )


print(
    "\n" + "=" * 60
)

print(
    "GRAPH COMPLETED"
)

print(
    "=" * 60
)