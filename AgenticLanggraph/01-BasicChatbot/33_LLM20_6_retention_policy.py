from datetime import datetime, timedelta


# ---------------------------------------------------------
# Retention policy
# ---------------------------------------------------------

RETENTION_DAYS = 30


def should_delete_thread(
    status: str,
    last_activity: datetime
) -> bool:

    now = datetime.now()

    age = now - last_activity

    print(f"Status       : {status}")
    print(f"Last activity: {last_activity}")
    print(f"Age (days)   : {age.days}")

    # Active conversations should always be retained
    if status == "ACTIVE":
        return False

    # Recently completed conversations are retained
    if status == "COMPLETED" and age.days <= RETENTION_DAYS:
        return False

    # Old completed conversations can be deleted
    if status == "COMPLETED" and age.days > RETENTION_DAYS:
        return True

    return False


# ---------------------------------------------------------
# Test 1: Active conversation
# ---------------------------------------------------------

active_thread = should_delete_thread(
    status="ACTIVE",
    last_activity=datetime.now() - timedelta(days=60)
)

print("\nTest 1")
print("Delete:", active_thread)


# ---------------------------------------------------------
# Test 2: Recently completed conversation
# ---------------------------------------------------------

recent_completed_thread = should_delete_thread(
    status="COMPLETED",
    last_activity=datetime.now() - timedelta(days=10)
)

print("\nTest 2")
print("Delete:", recent_completed_thread)


# ---------------------------------------------------------
# Test 3: Old completed conversation
# ---------------------------------------------------------

old_completed_thread = should_delete_thread(
    status="COMPLETED",
    last_activity=datetime.now() - timedelta(days=60)
)

print("\nTest 3")
print("Delete:", old_completed_thread)