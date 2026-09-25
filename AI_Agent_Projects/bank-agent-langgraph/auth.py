"""
auth.py
-------
Login verification. Deliberately not the AI agent's job — identity
checks should always be plain, predictable code.
"""

import psycopg2
import psycopg2.extras
from config import DATABASE_URL


def verify_login(customer_id: str, pin: str) -> dict | None:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT customer_id, name FROM customers WHERE customer_id = %s AND pin = %s",
        (customer_id, pin),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None
