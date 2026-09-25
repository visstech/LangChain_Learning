"""
tools.py
--------
The functions the agent can call, now wrapped with LangChain's @tool
decorator so they can be passed straight into create_agent().

SAME SECURITY PATTERN AS BEFORE: every tool only ever touches
CURRENT_CUSTOMER_ID — set once at login — never a customer ID the
agent could supply itself.
"""

import psycopg2
import psycopg2.extras
from langchain_core.tools import tool
from config import DATABASE_URL

CURRENT_CUSTOMER_ID = None


def _get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn


@tool
def get_balance() -> list:
    """Get the current balance of all accounts belonging to the logged-in customer."""
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT account_type, balance FROM accounts WHERE customer_id = %s",
        (CURRENT_CUSTOMER_ID,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


@tool
def get_recent_transactions(count: int = 5) -> list:
    """Get the logged-in customer's most recent transactions across all their accounts.

    Args:
        count: how many transactions to return.
    """
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT t.transaction_id, t.txn_date, t.description, t.amount, t.disputed
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE a.customer_id = %s
        ORDER BY t.txn_date DESC
        LIMIT %s
        """,
        (CURRENT_CUSTOMER_ID, count),
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


@tool
def block_card() -> dict:
    """Block the logged-in customer's card (e.g. lost or stolen). Irreversible —
    the agent must confirm with the customer in conversation before calling this."""
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cards SET status = 'blocked' WHERE customer_id = %s",
        (CURRENT_CUSTOMER_ID,),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "blocked", "message": "Your card has been blocked."}


@tool
def file_dispute(transaction_id: str, reason: str) -> dict:
    """File a dispute on a specific transaction. Must be confirmed with the
    customer first, since it starts a real review process.

    Args:
        transaction_id: ID of the transaction being disputed (from get_recent_transactions).
        reason: short description of why the customer is disputing it.
    """
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT t.transaction_id FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.transaction_id = %s AND a.customer_id = %s
        """,
        (transaction_id, CURRENT_CUSTOMER_ID),
    )
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        return {"error": "Transaction not found on your account."}

    cur.execute(
        "UPDATE transactions SET disputed = TRUE, dispute_status = 'under_review' "
        "WHERE transaction_id = %s",
        (transaction_id,),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {
        "status": "filed",
        "transaction_id": transaction_id,
        "message": "Dispute filed. A case manager will review it within 5 business days.",
    }


@tool
def get_dispute_status(transaction_id: str) -> dict:
    """Check the status of a previously filed dispute.

    Args:
        transaction_id: the transaction ID the customer is asking about.
    """
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT t.transaction_id, t.disputed, t.dispute_status
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.transaction_id = %s AND a.customer_id = %s
        """,
        (transaction_id, CURRENT_CUSTOMER_ID),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return {"error": "Transaction not found on your account."}
    if not row["disputed"]:
        return {"message": "No dispute has been filed for this transaction."}
    return {"transaction_id": transaction_id, "status": row["dispute_status"]}


@tool
def transfer_between_own_accounts(from_account_type: str, to_account_type: str, amount: float) -> dict:
    """Transfer money between the logged-in customer's OWN accounts
    (e.g. checking to savings). Must be confirmed with the customer
    first — this moves real balance.

    Args:
        from_account_type: 'checking' or 'savings' — where the money comes from.
        to_account_type: 'checking' or 'savings' — where the money goes.
        amount: how much to transfer.
    """
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT account_id, balance FROM accounts WHERE customer_id = %s AND account_type = %s",
        (CURRENT_CUSTOMER_ID, from_account_type),
    )
    from_acc = cur.fetchone()
    cur.execute(
        "SELECT account_id FROM accounts WHERE customer_id = %s AND account_type = %s",
        (CURRENT_CUSTOMER_ID, to_account_type),
    )
    to_acc = cur.fetchone()

    if from_acc is None or to_acc is None:
        cur.close()
        conn.close()
        return {"error": "One of those account types doesn't exist for this customer."}

    if from_acc["balance"] < amount:
        cur.close()
        conn.close()
        return {"error": "Insufficient funds for this transfer."}

    cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
                (amount, from_acc["account_id"]))
    cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
                (amount, to_acc["account_id"]))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "message": f"Transferred {amount} from {from_account_type} to {to_account_type}."}


@tool
def update_phone_number(new_phone: str) -> dict:
    """Update the logged-in customer's contact phone number. Must be
    confirmed with the customer first.

    Args:
        new_phone: the new phone number, including country code.
    """
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE customers SET phone_number = %s WHERE customer_id = %s",
        (new_phone, CURRENT_CUSTOMER_ID),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "updated", "new_phone": new_phone}


@tool
def list_upcoming_bills() -> list:
    """List the logged-in customer's unpaid upcoming bills."""
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT payee, amount, due_date FROM bills WHERE customer_id = %s AND paid = FALSE "
        "ORDER BY due_date ASC",
        (CURRENT_CUSTOMER_ID,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


ALL_TOOLS = [
    get_balance,
    get_recent_transactions,
    block_card,
    file_dispute,
    get_dispute_status,
    transfer_between_own_accounts,
    update_phone_number,
    list_upcoming_bills,
]
