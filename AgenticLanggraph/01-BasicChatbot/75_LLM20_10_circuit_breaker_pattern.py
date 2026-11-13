
"""
LESSON 75: CIRCUIT BREAKER PATTERN IN LANGGRAPH WORKFLOWS

PURPOSE
-------
Learn how a circuit breaker protects a workflow from repeatedly
calling an unhealthy external service.

WHAT THIS PROGRAM DOES
----------------------
1. Starts with the circuit in CLOSED state.
2. Simulates two consecutive service failures.
3. Opens the circuit after the failure threshold is reached.
4. Blocks the next request without calling the service.
5. Allows a controlled recovery test in HALF_OPEN state.
6. Closes the circuit when the recovery test succeeds.

KEY CONCEPTS
------------
- CLOSED: Requests are allowed.
- OPEN: Requests are blocked.
- HALF_OPEN: A controlled recovery request is allowed.
- StateGraph: Defines the workflow.
- Conditional edges: Route requests based on circuit state.
- State carried between invocations: Preserves the circuit status
  for this learning example.

EXPECTED FLOW
-------------
Request 1: Failure -> CLOSED
Request 2: Failure -> OPEN
Request 3: Blocked -> OPEN
Request 4: Recovery succeeds -> CLOSED

NOTE
----
This is a learning simulation. The circuit state is carried forward
by our Python program. A production system needs shared, durable
state management when multiple workers or application instances
must use the same circuit breaker.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ---------------------------------------------------------
# STEP 1: DEFINE THE WORKFLOW STATE
# ---------------------------------------------------------

class CircuitBreakerState(TypedDict):
    request_id: str
    service_should_fail: bool
    allow_recovery_test: bool

    circuit_state: str
    failure_count: int
    failure_threshold: int

    request_allowed: bool
    service_result: str


# ---------------------------------------------------------
# STEP 2: CHECK THE CIRCUIT STATE
# ---------------------------------------------------------

def check_circuit(state: CircuitBreakerState):

    circuit_state = state["circuit_state"]
    allow_recovery_test = state["allow_recovery_test"]

    print("\nChecking circuit breaker...")

    # OPEN state normally blocks all requests.
    # A recovery test can move the circuit into HALF_OPEN.
    if circuit_state == "OPEN":

        if allow_recovery_test:

            print("Circuit OPEN -> HALF_OPEN")
            return {
                "circuit_state": "HALF_OPEN",
                "request_allowed": True
            }

        print("Circuit is OPEN. Request will be blocked.")

        return {
            "request_allowed": False
        }

    # CLOSED and HALF_OPEN allow a request.
    print(f"Circuit state: {circuit_state}")

    return {
        "request_allowed": True
    }


# ---------------------------------------------------------
# STEP 3: CALL THE SIMULATED EXTERNAL SERVICE
# ---------------------------------------------------------

def call_service(state: CircuitBreakerState):

    print("Calling external service...")

    if state["service_should_fail"]:

        print("External service FAILED!")

        new_failure_count = state["failure_count"] + 1

        # Open the circuit when the threshold is reached.
        if (
            new_failure_count >= state["failure_threshold"]
            or state["circuit_state"] == "HALF_OPEN"
        ):

            print("Failure threshold reached. Opening circuit.")

            return {
                "failure_count": new_failure_count,
                "circuit_state": "OPEN",
                "service_result": "SERVICE FAILED - CIRCUIT OPEN"
            }

        return {
            "failure_count": new_failure_count,
            "service_result": "SERVICE FAILED - CIRCUIT CLOSED"
        }

    # Successful service call resets the failure count.
    print("External service SUCCESS!")

    return {
        "failure_count": 0,
        "circuit_state": "CLOSED",
        "service_result": "SERVICE SUCCESS"
    }


# ---------------------------------------------------------
# STEP 4: BLOCK THE REQUEST
# ---------------------------------------------------------

def block_request(state: CircuitBreakerState):

    print("Request blocked. External service was NOT called.")

    return {
        "service_result": "REQUEST BLOCKED - CIRCUIT OPEN"
    }


# ---------------------------------------------------------
# STEP 5: DEFINE CONDITIONAL ROUTING
# ---------------------------------------------------------

def route_after_check(state: CircuitBreakerState):

    if state["request_allowed"]:
        return "call_service"

    return "block_request"


# ---------------------------------------------------------
# STEP 6: BUILD THE LANGGRAPH WORKFLOW
# ---------------------------------------------------------

builder = StateGraph(CircuitBreakerState)

builder.add_node("check_circuit", check_circuit)
builder.add_node("call_service", call_service)
builder.add_node("block_request", block_request)

builder.add_edge(START, "check_circuit")

builder.add_conditional_edges(
    "check_circuit",
    route_after_check,
    {
        "call_service": "call_service",
        "block_request": "block_request"
    }
)

builder.add_edge("call_service", END)
builder.add_edge("block_request", END)

graph = builder.compile()


# ---------------------------------------------------------
# STEP 7: INITIALIZE THE CIRCUIT BREAKER
# ---------------------------------------------------------

state = {
    "request_id": "",
    "service_should_fail": False,
    "allow_recovery_test": False,

    "circuit_state": "CLOSED",
    "failure_count": 0,
    "failure_threshold": 3,

    "request_allowed": False,
    "service_result": ""
}


# ---------------------------------------------------------
# STEP 8: SIMULATE FOUR REQUESTS
# ---------------------------------------------------------

test_requests = [
    {
        "request_id": "REQ001",
        "service_should_fail": True,
        "allow_recovery_test": False
    },
    {
        "request_id": "REQ002",
        "service_should_fail": True,
        "allow_recovery_test": False
    },
    {
    "request_id": "REQ003",
    "service_should_fail": True,
    "allow_recovery_test": False
    },
    {
    "request_id": "REQ004",
    "service_should_fail": False,
    "allow_recovery_test": False
    },
    {
    "request_id": "REQ005",
    "service_should_fail": False,
    "allow_recovery_test": True
    }
]


print("=" * 65)
print("LESSON 75: CIRCUIT BREAKER PATTERN")
print("=" * 65)

for request in test_requests:

    # Update the request-specific inputs.
    # Preserve the circuit state and failure count.
    state.update(request)

    print("\n" + "=" * 65)
    print(f"PROCESSING REQUEST: {state['request_id']}")
    print("=" * 65)

    state = graph.invoke(state)

    print("\nREQUEST RESULT")
    print("-" * 65)
    print(f"Request ID     : {state['request_id']}")
    print(f"Circuit State  : {state['circuit_state']}")
    print(f"Failure Count  : {state['failure_count']}")
    print(f"Service Result : {state['service_result']}")


print("\n" + "=" * 65)
print("FINAL CIRCUIT BREAKER STATUS")
print("=" * 65)

print(f"Circuit State : {state['circuit_state']}")
print(f"Failure Count : {state['failure_count']}")
print("Lesson 75 completed.")
