from auth.session import Session
from agent.insurance_agent import InsuranceAgent


# --------------------------------------------------
# Login
# --------------------------------------------------

session = Session("CUST001")

print(
    "Logged in as:",
    session.get_user_id()
)


# --------------------------------------------------
# Create Agent ONCE
# --------------------------------------------------

agent = InsuranceAgent(session)


# --------------------------------------------------
# Conversation loop
# --------------------------------------------------

while True:

    user_message = input(
        "\nYou ('exit' to stop): "
    )

    if user_message.lower() == "exit":
        break

    response = agent.invoke(
        user_message
    )

    print("\nLLM Response:")
    print(response)