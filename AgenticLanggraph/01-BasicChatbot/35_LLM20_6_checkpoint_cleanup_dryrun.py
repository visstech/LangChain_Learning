"""
===============================================================
LangGraph 20.6.4 - PostgreSQL Checkpoint Cleanup (DRY RUN)
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates a safe, production-style approach to
cleaning up old LangGraph checkpoint threads.

It does NOT delete anything from PostgreSQL.

Instead, it:

1. Defines a retention policy.
2. Checks which threads are expired.
3. Runs in DRY-RUN mode.
4. Shows which threads WOULD be deleted.
5. Protects ACTIVE threads from deletion.

WHY ARE WE USING DRY RUN?
-------------------------
A cleanup job can be destructive.

Before allowing a production job to delete checkpoint data,
we should first run it in "dry-run" mode and review the
candidate threads.

IMPORTANT:
-----------
checkpointer.delete_thread(thread_id)

deletes the checkpoint history associated with that entire
thread_id.

Therefore, we must be careful before executing it.

RETENTION POLICY USED IN THIS LESSON
------------------------------------
ACTIVE
    -> Never delete

COMPLETED + age <= 30 days
    -> Keep

COMPLETED + age > 30 days
    -> Eligible for deletion

LEARNING GOAL
-------------
Understand the separation between:

    RETENTION DECISION
            +
    DELETE OPERATION

The retention logic decides WHAT may be deleted.
The actual delete operation is a separate step.

===============================================================
"""

from datetime import datetime, timedelta

from langgraph.checkpoint.postgres import PostgresSaver


# =============================================================
# 1. Configuration
# =============================================================

RETENTION_DAYS = 30

# IMPORTANT:
# Set this to False while testing.
#
# False = DRY RUN
# True  = ACTUAL deletion
#
# We will keep this False for this lesson.
DRY_RUN = True


# PostgreSQL database used in our LangGraph persistence lessons.
DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


# =============================================================
# 2. Retention decision function
# =============================================================

def should_delete_thread(
    status: str,
    last_activity: datetime
) -> bool:
    """
    Decide whether a thread is eligible for cleanup.

    This function ONLY makes the decision.
    It does not delete anything.

    Rules:
        ACTIVE
            -> Keep

        COMPLETED and <= 30 days old
            -> Keep

        COMPLETED and > 30 days old
            -> Delete candidate
    """

    now = datetime.now()

    age = now - last_activity

    # Active conversations must be retained.
    if status == "ACTIVE":
        return False

    # Recently completed conversations are retained.
    if status == "COMPLETED" and age.days <= RETENTION_DAYS:
        return False

    # Old completed conversations are eligible for cleanup.
    if status == "COMPLETED" and age.days > RETENTION_DAYS:
        return True

    # Unknown status -> safest action is KEEP.
    return False


# =============================================================
# 3. Simulated thread records
# =============================================================

threads = [
    {
        "thread_id": "thread-001",
        "status": "ACTIVE",
        "last_activity": datetime.now() - timedelta(days=60),
    },
    {
        "thread_id": "thread-002",
        "status": "COMPLETED",
        "last_activity": datetime.now() - timedelta(days=10),
    },
    {
        "thread_id": "thread-003",
        "status": "COMPLETED",
        "last_activity": datetime.now() - timedelta(days=60),
    },
    {
        "thread_id": "thread-004",
        "status": "COMPLETED",
        "last_activity": datetime.now() - timedelta(days=45),
    },
    {
        "thread_id": "thread-005",
        "status": "ACTIVE",
        "last_activity": datetime.now() - timedelta(days=90),
    },
]


# =============================================================
# 4. Start PostgreSQL checkpointer
# =============================================================

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    print("=" * 60)
    print("LangGraph Checkpoint Cleanup - DRY RUN")
    print("=" * 60)

    print(f"Retention period : {RETENTION_DAYS} days")
    print(f"DRY_RUN          : {DRY_RUN}")

    print("\nScanning threads...\n")


    # =========================================================
    # 5. Evaluate each thread
    # =========================================================

    for thread in threads:

        thread_id = thread["thread_id"]
        status = thread["status"]
        last_activity = thread["last_activity"]

        age = datetime.now() - last_activity

        delete_candidate = should_delete_thread(
            status=status,
            last_activity=last_activity,
        )

        print(
            f"{thread_id} | "
            f"Status={status} | "
            f"Age={age.days} days | "
            f"DeleteCandidate={delete_candidate}"
        )


        # =====================================================
        # 6. DRY-RUN cleanup
        # =====================================================

        if delete_candidate:

            if DRY_RUN:

                print(
                    f"   [DRY RUN] Would delete: {thread_id}"
                )

            else:

                print(
                    f"   Deleting thread: {thread_id}"
                )

                checkpointer.delete_thread(
                    thread_id
                )


    # =========================================================
    # 7. Completion message
    # =========================================================

    print("\n" + "=" * 60)

    if DRY_RUN:

        print(
            "DRY RUN completed - no threads were deleted."
        )

    else:

        print(
            "Cleanup completed - eligible threads deleted."
        )

    print("=" * 60)