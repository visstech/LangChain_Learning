"""
auth.py
-------
Handles login. This is deliberately NOT something the AI agent does —
identity verification should always be handled by traditional,
predictable code, not an LLM. The agent only ever starts working
after this code has already confirmed who it's talking to.
"""

import sqlite3
from database import DB_FILE


def verify_login(customer_id: str, pin: str) -> dict | None:
    """
    Checks customer_id + pin against the database.
    Returns the customer's info dict if valid, or None if not.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT customer_id, name FROM customers WHERE customer_id = ? AND pin = ?",
        (customer_id, pin),
    ).fetchone()
    conn.close()

    return dict(row) if row else None
