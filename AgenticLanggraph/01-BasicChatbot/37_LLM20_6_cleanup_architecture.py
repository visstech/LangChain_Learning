"""
===============================================================
LangGraph 20.6.6 - Cleanup Architecture
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates a production-style cleanup design
for LangGraph checkpoint threads.

It intentionally separates:

    1. Candidate selection
    2. Candidate review
    3. Deletion
    4. Verification

WHY IS THIS IMPORTANT?
----------------------
Deleting LangGraph checkpoints is a destructive operation.

Instead of doing this:

    Find candidate -> Delete immediately

we use:

    Find candidate
          ↓
       Review
          ↓
      Approve
          ↓
       Delete
          ↓
      Verify

LEARNING GOAL
-------------
Understand how a production cleanup process can separate
decision-making from destructive operations.

RETENTION POLICY
----------------
ACTIVE
    -> Keep

COMPLETED <= 30 days
    -> Keep

COMPLETED > 30 days
    -> Cleanup candidate

IMPORTANT
---------
This exercise uses simulated thread records.

No PostgreSQL data is deleted by this program.

===============================================================
"""

from datetime import datetime, timedelta


# =============================================================
# 1. Configuration
# =============================================================

RETENTION_DAYS = 30


# =============================================================
# 2. Simulated thread records
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
# 3. Candidate selection
# =============================================================

def find_cleanup_candidates(threads):
    """
    Identify threads that are eligible for cleanup.

    IMPORTANT:
    This function ONLY identifies candidates.

    It does NOT delete anything.
    """

    candidates = []

    for thread in threads:

        age = (
            datetime.now()
            - thread["last_activity"]
        ).days

        # Active conversations are protected.
        if thread["status"] == "ACTIVE":
            continue

        # Recently completed conversations are retained.
        if (
            thread["status"] == "COMPLETED"
            and age <= RETENTION_DAYS
        ):
            continue

        # Old completed conversations become candidates.
        if (
            thread["status"] == "COMPLETED"
            and age > RETENTION_DAYS
        ):
            candidates.append(thread)

    return candidates


# =============================================================
# 4. Select cleanup candidates
# =============================================================

candidates = find_cleanup_candidates(threads)


print("=" * 60)
print("STEP 1 - CLEANUP CANDIDATE SELECTION")
print("=" * 60)

for thread in candidates:

    print(
        f"{thread['thread_id']} | "
        f"{thread['status']}"
    )


# =============================================================
# 5. Review candidates
# =============================================================

print("\n" + "=" * 60)
print("STEP 2 - CANDIDATE REVIEW")
print("=" * 60)

print(
    "Candidates identified:"
)

for thread in candidates:

    print(
        f"Review required -> "
        f"{thread['thread_id']}"
    )


# =============================================================
# 6. Explicit approval
# =============================================================

# In a real production system this approval could come from:
#
# - an administrator
# - a scheduled cleanup policy
# - an operations workflow
# - a monitoring system
#
# For this learning exercise we explicitly define the
# approved thread IDs.

approved_thread_ids = {
    "thread-003"
}


print("\n" + "=" * 60)
print("STEP 3 - APPROVED THREADS")
print("=" * 60)

for thread_id in approved_thread_ids:

    print(
        f"Approved -> {thread_id}"
    )


# =============================================================
# 7. Determine what would be deleted
# =============================================================

print("\n" + "=" * 60)
print("STEP 4 - DELETE PLAN")
print("=" * 60)

for thread in candidates:

    thread_id = thread["thread_id"]

    if thread_id in approved_thread_ids:

        print(
            f"DELETE -> {thread_id}"
        )

    else:

        print(
            f"KEEP -> {thread_id}"
        )


# =============================================================
# 8. Final safety summary
# =============================================================

print("\n" + "=" * 60)
print("CLEANUP SUMMARY")
print("=" * 60)

print(
    f"Total threads       : {len(threads)}"
)

print(
    f"Cleanup candidates  : {len(candidates)}"
)

print(
    f"Approved deletions  : "
    f"{len(approved_thread_ids)}"
)

print(
    "\nNo actual deletion was performed."
)

print(
    "This program demonstrates the cleanup architecture only."
)