from langgraph.checkpoint.postgres import PostgresSaver


DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    checkpointer.setup()

    thread_id = "expense-001"

    print(f"\n🗑️ Deleting thread: {thread_id}")

    checkpointer.delete_thread(thread_id)

    print("✅ Thread deleted successfully.")