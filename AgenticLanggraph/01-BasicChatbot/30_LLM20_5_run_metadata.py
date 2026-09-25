from langgraph.checkpoint.postgres import PostgresSaver


DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    config = {
        "configurable": {
            "thread_id": "expense-run-test"
        }
    }

    print("\n🔍 CHECKPOINT HISTORY")

    checkpoints = list(
        checkpointer.list(config)
    )

    for i, checkpoint in enumerate(checkpoints, start=1):

        print(f"\nCheckpoint {i}")
        print("-" * 50)

        print("Config:")
        print(checkpoint.config)

        print("\nMetadata:")
        print(checkpoint.metadata)

        print("\nParent Config:")
        print(checkpoint.parent_config)