from langgraph.checkpoint.postgres import PostgresSaver
import inspect

DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    print("\n🔍 DELETE_FOR_RUNS SIGNATURE")
    print(inspect.signature(checkpointer.delete_for_runs))

    print("\n📖 DELETE_FOR_RUNS DOCUMENTATION")
    print(checkpointer.delete_for_runs.__doc__)