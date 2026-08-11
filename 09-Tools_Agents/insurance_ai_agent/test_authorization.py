from authorization import authorize_customer_access


authenticated_user = "CUST001"


print("Test 1: Own customer")

result = authorize_customer_access(
    authenticated_user,
    "CUST001"
)

print("Access:", result)


print("\nTest 2: Another customer")

result = authorize_customer_access(
    authenticated_user,
    "CUST002"
)

print("Access:", result)