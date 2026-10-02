"""
===============================================================
LangGraph 20.6.7 - Idempotent Cleanup & Verification
===============================================================

WHAT DOES THIS PROGRAM DO?
--------------------------
This program demonstrates an important production concept:

    IDEMPOTENT CLEANUP

A cleanup operation is idempotent when running it multiple
times does not create an unexpected problem.

Example:

    First execution:
        thread-003 -> deleted

    Second execution:
        thread-003 -> already deleted
        -> safely skipped

This program simulates that behavior.

PRODUCTION CLEANUP FLOW
-----------------------
    1. Identify cleanup candidate
    2. Check whether thread still exists
    3. Delete if it exists
    4. Verify deletion
    5. If cleanup runs again, safely skip the missing thread

IMPORTANT
---------
This lesson uses an in-memory Python set to simulate existing
threads.

No PostgreSQL data is deleted by this program.

LEARNING GOAL
-------------
Understand how production cleanup jobs should safely handle:

    - retries
    - duplicate execution
    - already-deleted threads
    - post-delete verification

===============================================================
"""


# =============================================================
# 1. Simulated existing threads
# =============================================================

existing_threads = {
    "thread-001",
    "thread-002",
    "thread-003",
    "thread-004",
    "thread-005",
}


# =============================================================
# 2. Cleanup function
# =============================================================

def cleanup_thread(thread_id: str):
    """
    Delete a thread only if it currently exists.

    If the thread is already absent, safely skip it.

    This makes the cleanup operation idempotent.
    """

    print(f"\nCleanup request: {thread_id}")

    # ---------------------------------------------------------
    # Check whether the thread exists
    # ---------------------------------------------------------
    if thread_id not in existing_threads:

        print(
            f"SKIP: {thread_id} "
            f"does not exist."
        )

        return False


    # ---------------------------------------------------------
    # Delete the thread
    # ---------------------------------------------------------
    existing_threads.remove(thread_id)

    print(
        f"DELETED: {thread_id}"
    )

    return True


# =============================================================
# 3. First cleanup attempt
# =============================================================

print("=" * 60)
print("FIRST CLEANUP")
print("=" * 60)

cleanup_thread(
    "thread-003"
)


# =============================================================
# 4. Verify first cleanup
# =============================================================

print("\n" + "=" * 60)
print("FIRST VERIFICATION")
print("=" * 60)

if "thread-003" not in existing_threads:

    print(
        "✅ thread-003 no longer exists."
    )

else:

    print(
        "❌ thread-003 still exists."
    )


# =============================================================
# 5. Second cleanup attempt
# =============================================================

print("\n" + "=" * 60)
print("SECOND CLEANUP - RETRY")
print("=" * 60)

cleanup_thread(
    "thread-003"
)


# =============================================================
# 6. Final verification
# =============================================================

print("\n" + "=" * 60)
print("FINAL VERIFICATION")
print("=" * 60)

if "thread-003" not in existing_threads:

    print(
        "✅ thread-003 remains deleted."
    )

else:

    print(
        "❌ thread-003 unexpectedly exists."
    )


# =============================================================
# 7. Show remaining threads
# =============================================================

print("\nRemaining threads:")

for thread_id in sorted(existing_threads):

    print(
        f"  {thread_id}"
    )


# =============================================================
# 8. Final result
# =============================================================

print("\n" + "=" * 60)
print("IDEMPOTENT CLEANUP RESULT")
print("=" * 60)

print(
    "✅ First cleanup deleted the thread."
)

print(
    "✅ Second cleanup safely skipped it."
)

print(
    "✅ Cleanup is idempotent."
)