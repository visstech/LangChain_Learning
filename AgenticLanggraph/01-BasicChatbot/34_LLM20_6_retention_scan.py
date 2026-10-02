from datetime import datetime, timedelta


RETENTION_DAYS = 30


def should_delete_thread(
    status: str,
    last_activity: datetime
) -> bool:

    now = datetime.now()
    age = now - last_activity

    if status == "ACTIVE":
        return False

    if status == "COMPLETED" and age.days <= RETENTION_DAYS:
        return False

    if status == "COMPLETED" and age.days > RETENTION_DAYS:
        return True

    return False


# ---------------------------------------------------------
# Simulated thread records
# ---------------------------------------------------------

threads = [
    {
        "thread_id": "thread-001",
        "status": "ACTIVE",
        "last_activity": datetime.now() - timedelta(days=60)
    },
    {
        "thread_id": "thread-002",
        "status": "COMPLETED",
        "last_activity": datetime.now() - timedelta(days=10)
    },
    {
        "thread_id": "thread-003",
        "status": "COMPLETED",
        "last_activity": datetime.now() - timedelta(days=60)
    },
    {
        "thread_id": "thread-004",
        "status": "COMPLETED",
        "last_activity": datetime.now() - timedelta(days=45)
    },
    {
        "thread_id": "thread-005",
        "status": "ACTIVE",
        "last_activity": datetime.now() - timedelta(days=90)
    }
]


# ---------------------------------------------------------
# Scan threads
# ---------------------------------------------------------

print("Retention Scan\n")

for thread in threads:

    delete = should_delete_thread(
        thread["status"],
        thread["last_activity"]
    )

    print(
        f"{thread['thread_id']} | "
        f"{thread['status']} | "
        f"Delete={delete}"
    )