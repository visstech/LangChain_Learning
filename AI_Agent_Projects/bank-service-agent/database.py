"""
database.py
-----------
Creates and seeds a small SQLite database that simulates a bank's
records. This is entirely fake data on your own machine — this
project never connects to any real bank.

Run this file once before starting the app: python database.py
"""

import sqlite3

DB_FILE = "bank.db"


def init_db():
    """Creates all tables and wipes any existing data (fresh start)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.executescript("""
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS accounts;
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS cards;

        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            pin TEXT NOT NULL
        );

        CREATE TABLE accounts (
            account_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            disputed INTEGER DEFAULT 0,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        );

        CREATE TABLE cards (
            card_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            last_four TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
    """)

    # --- Sample customer 1 ---
    c.execute("INSERT INTO customers VALUES (?, ?, ?)", ("cust001", "Priya Sharma", "1234"))
    c.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)", ("acc001", "cust001", "checking", 2450.75))
    c.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)", ("acc002", "cust001", "savings", 8900.00))
    c.execute("INSERT INTO cards VALUES (?, ?, ?, ?)", ("card001", "cust001", "4821", "active"))

    transactions_1 = [
        ("t001", "acc001", "2026-08-20", "Grocery Store", -85.40),
        ("t002", "acc001", "2026-08-19", "Salary Deposit", 3200.00),
        ("t003", "acc001", "2026-08-18", "Electric Bill", -120.00),
        ("t004", "acc001", "2026-08-17", "Coffee Shop", -6.50),
        ("t005", "acc001", "2026-08-15", "Unknown Merchant XZ99", -450.00),
    ]
    c.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, 0)", transactions_1)

    # --- Sample customer 2 ---
    c.execute("INSERT INTO customers VALUES (?, ?, ?)", ("cust002", "Ahmad Faizal", "5678"))
    c.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)", ("acc003", "cust002", "checking", 610.20))
    c.execute("INSERT INTO cards VALUES (?, ?, ?, ?)", ("card002", "cust002", "9034", "active"))

    transactions_2 = [
        ("t006", "acc003", "2026-08-21", "Online Store", -45.00),
        ("t007", "acc003", "2026-08-20", "Salary Deposit", 1800.00),
        ("t008", "acc003", "2026-08-19", "Restaurant", -32.10),
    ]
    c.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, 0)", transactions_2)

    conn.commit()
    conn.close()
    print(f"Database created: {DB_FILE}")
    print("Sample logins -> customer_id: cust001, pin: 1234 (Senthil)")
    print("             -> customer_id: cust002, pin: 5678 (Pavan)")


if __name__ == "__main__":
    init_db()
