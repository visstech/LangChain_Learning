from authorization import authorize_customer_access


customer_database = {

    "CUST001": {
        "Name": "Senthil",
        "Policy": "Motor Insurance",
        "Status": "Active"
    },

    "CUST002": {
        "Name": "Ramesh",
        "Policy": "Travel Insurance",
        "Status": "Expired"
    }

}


def get_customer_policy_for_user(
    authenticated_user_id,
    requested_customer_id
):

    allowed = authorize_customer_access(
        authenticated_user_id,
        requested_customer_id
    )

    if not allowed:

        return "Access denied."

    customer = customer_database.get(
        requested_customer_id.upper()
    )

    if customer:

        return str(customer)

    return "Customer not found."


# =====================================================
# Test 1
# =====================================================

print("\nTest 1: User accesses own policy")

result = get_customer_policy_for_user(
    "CUST001",
    "CUST001"
)

print("Result:", result)


# =====================================================
# Test 2
# =====================================================

print("\nTest 2: User tries another customer's policy")

result = get_customer_policy_for_user(
    "CUST001",
    "CUST002"
)

print("Result:", result)