"""
tools.py
--------
These are the functions the AI agent is allowed to call. This is the
most important file in the project from a security-design standpoint,
so read the comments carefully.

KEY PRINCIPLE: every function here only ever reads or changes data
belonging to CURRENT_CUSTOMER_ID — the customer who is currently
logged in. The agent is never given a customer_id parameter to fill
in itself. If it could, a malicious or confused prompt might trick it
into looking up someone else's account. Instead, the app sets
CURRENT_CUSTOMER_ID once at login, and every tool silently scopes
itself to that value.
"""

import sqlite3
from database import DB_FILE

# Set once by app.py right after a successful login.
CURRENT_CUSTOMER_ID = None


def _get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def get_balance() -> list:
    """
    Get the current balance of all accounts belonging to the logged-in
    customer.

    Returns a list of dicts like:
    [{"account_type": "checking", "balance": 2450.75}, ...]
    """
    conn = _get_connection()
    rows = conn.execute(
        "SELECT account_type, balance FROM accounts WHERE customer_id = ?",
        (CURRENT_CUSTOMER_ID,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_recent_transactions(count: int = 5) -> list:
    """
    Get the logged-in customer's most recent transactions across all
    their accounts.

    Args:
        count: how many transactions to return.

    Returns a list of dicts like:
    [{"transaction_id": "t001", "date": "2026-08-20",
      "description": "Grocery Store", "amount": -85.40}, ...]
    """
    conn = _get_connection()
    rows = conn.execute(
        """
        SELECT t.transaction_id, t.date, t.description, t.amount, t.disputed
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE a.customer_id = ?
        ORDER BY t.date DESC
        LIMIT ?
        """,
        (CURRENT_CUSTOMER_ID, count),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def block_card() -> dict:
    """
    Block the logged-in customer's card, e.g. because it's lost or
    stolen. This is an IRREVERSIBLE ACTION in a real bank, so the
    agent's instructions require it to confirm with the customer in
    plain conversation before ever calling this.

    Returns a dict confirming the new status.
    """
    conn = _get_connection()
    conn.execute(
        "UPDATE cards SET status = 'blocked' WHERE customer_id = ?",
        (CURRENT_CUSTOMER_ID,),
    )
    conn.commit()
    conn.close()
    return {"status": "blocked", "message": "Your card has been blocked."}


def file_dispute(transaction_id: str, reason: str) -> dict:
    """
    File a dispute on a specific transaction, e.g. if the customer
    doesn't recognize a charge. Like block_card, this is an action
    with real consequences, so the agent must confirm details with
    the customer first.

    Args:
        transaction_id: the ID of the transaction being disputed
                         (the agent gets this from get_recent_transactions).
        reason: a short description of why the customer is disputing it.

    Returns a dict confirming the dispute was filed.
    """
    conn = _get_connection()

    # Security check: make sure this transaction actually belongs to
    # the logged-in customer before touching it.
    row = conn.execute(
        """
        SELECT t.transaction_id FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.transaction_id = ? AND a.customer_id = ?
        """,
        (transaction_id, CURRENT_CUSTOMER_ID),
    ).fetchone()

    if row is None:
        conn.close()
        return {"error": "Transaction not found on your account."}

    conn.execute(
        "UPDATE transactions SET disputed = 1 WHERE transaction_id = ?",
        (transaction_id,),
    )
    conn.commit()
    conn.close()
    return {
        "status": "filed",
        "transaction_id": transaction_id,
        "message": "Dispute filed. A case manager will review it within 5 business days.",
    }
