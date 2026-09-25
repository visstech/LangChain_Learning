"""
database.py
-----------
Creates and seeds the PostgreSQL database. Run this once before
starting the app: python database.py

Requires Postgres to already be running — see README.md for the
docker compose command.
"""

import psycopg2
from config import DATABASE_URL


def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS bills CASCADE;
        DROP TABLE IF EXISTS transactions CASCADE;
        DROP TABLE IF EXISTS cards CASCADE;
        DROP TABLE IF EXISTS accounts CASCADE;
        DROP TABLE IF EXISTS customers CASCADE;

        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            pin TEXT NOT NULL,
            phone_number TEXT
        );

        CREATE TABLE accounts (
            account_id TEXT PRIMARY KEY,
            customer_id TEXT REFERENCES customers(customer_id),
            account_type TEXT NOT NULL,
            balance NUMERIC NOT NULL
        );

        CREATE TABLE transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT REFERENCES accounts(account_id),
            txn_date DATE NOT NULL,
            description TEXT NOT NULL,
            amount NUMERIC NOT NULL,
            disputed BOOLEAN DEFAULT FALSE,
            dispute_status TEXT
        );

        CREATE TABLE cards (
            card_id TEXT PRIMARY KEY,
            customer_id TEXT REFERENCES customers(customer_id),
            last_four TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );

        CREATE TABLE bills (
            bill_id TEXT PRIMARY KEY,
            customer_id TEXT REFERENCES customers(customer_id),
            payee TEXT NOT NULL,
            amount NUMERIC NOT NULL,
            due_date DATE NOT NULL,
            paid BOOLEAN DEFAULT FALSE
        );
    """)

    # --- Sample customer 1 ---
    cur.execute("INSERT INTO customers VALUES (%s, %s, %s, %s)",
                ("cust001", "Priya Sharma", "1234", "+60123456789"))
    cur.execute("INSERT INTO accounts VALUES (%s, %s, %s, %s)",
                ("acc001", "cust001", "checking", 2450.75))
    cur.execute("INSERT INTO accounts VALUES (%s, %s, %s, %s)",
                ("acc002", "cust001", "savings", 8900.00))
    cur.execute("INSERT INTO cards VALUES (%s, %s, %s, %s)",
                ("card001", "cust001", "4821", "active"))

    txns_1 = [
        ("t001", "acc001", "2026-08-20", "Grocery Store", -85.40),
        ("t002", "acc001", "2026-08-19", "Salary Deposit", 3200.00),
        ("t003", "acc001", "2026-08-18", "Electric Bill", -120.00),
        ("t004", "acc001", "2026-08-17", "Coffee Shop", -6.50),
        ("t005", "acc001", "2026-08-15", "Unknown Merchant XZ99", -450.00),
    ]
    cur.executemany(
        "INSERT INTO transactions (transaction_id, account_id, txn_date, description, amount) "
        "VALUES (%s, %s, %s, %s, %s)",
        txns_1,
    )

    bills_1 = [
        ("b001", "cust001", "City Water Utility", 45.00, "2026-08-28"),
        ("b002", "cust001", "Internet Provider", 79.90, "2026-09-02"),
    ]
    cur.executemany(
        "INSERT INTO bills (bill_id, customer_id, payee, amount, due_date) "
        "VALUES (%s, %s, %s, %s, %s)",
        bills_1,
    )

    # --- Sample customer 2 ---
    cur.execute("INSERT INTO customers VALUES (%s, %s, %s, %s)",
                ("cust002", "Ahmad Faizal", "5678", "+60129876543"))
    cur.execute("INSERT INTO accounts VALUES (%s, %s, %s, %s)",
                ("acc003", "cust002", "checking", 610.20))
    cur.execute("INSERT INTO cards VALUES (%s, %s, %s, %s)",
                ("card002", "cust002", "9034", "active"))

    txns_2 = [
        ("t006", "acc003", "2026-08-21", "Online Store", -45.00),
        ("t007", "acc003", "2026-08-20", "Salary Deposit", 1800.00),
        ("t008", "acc003", "2026-08-19", "Restaurant", -32.10),
    ]
    cur.executemany(
        "INSERT INTO transactions (transaction_id, account_id, txn_date, description, amount) "
        "VALUES (%s, %s, %s, %s, %s)",
        txns_2,
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Database created and seeded.")
    print("Sample logins -> cust001 / 1234 (Priya)  |  cust002 / 5678 (Ahmad)")


if __name__ == "__main__":
    init_db()
