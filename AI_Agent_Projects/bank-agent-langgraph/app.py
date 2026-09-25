"""
app.py
------
Streamlit web app. Run with: streamlit run app.py
"""

import streamlit as st
from auth import verify_login
import tools
from agent import send_message

st.set_page_config(page_title="Bank Assistant", page_icon="🏦")


def login_screen():
    st.title("🏦 Bank Assistant — Sign In")
    st.caption("Simulated bank for a portfolio project — not a real bank.")

    customer_id = st.text_input("Customer ID")
    pin = st.text_input("PIN", type="password")

    if st.button("Sign In"):
        customer = verify_login(customer_id, pin)
        if customer:
            tools.CURRENT_CUSTOMER_ID = customer["customer_id"]
            st.session_state.customer = customer
            st.session_state.messages = []
            st.rerun()
        else:
            st.error("Invalid customer ID or PIN.")

    with st.expander("Sample logins for testing"):
        st.write("customer_id: `cust001`, PIN: `1234` (Priya Sharma)")
        st.write("customer_id: `cust002`, PIN: `5678` (Ahmad Faizal)")


def chat_screen():
    customer = st.session_state.customer
    st.title("🏦 Bank Assistant")
    st.caption(f"Signed in as {customer['name']}")

    if st.button("Sign out"):
        for key in ["customer", "messages"]:
            del st.session_state[key]
        tools.CURRENT_CUSTOMER_ID = None
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask about your account...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Make sure the tools are scoped to this customer before
                # the agent runs, in case Streamlit reran the script.
                tools.CURRENT_CUSTOMER_ID = customer["customer_id"]
                reply = send_message(customer["customer_id"], user_input)
                st.write(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})


if "customer" not in st.session_state:
    login_screen()
else:
    chat_screen()
