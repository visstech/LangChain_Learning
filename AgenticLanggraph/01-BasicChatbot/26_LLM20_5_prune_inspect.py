from langgraph.checkpoint.postgres import PostgresSaver
import inspect

DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    print("\n🔍 PRUNE SIGNATURE")
    print(inspect.signature(checkpointer.prune))

    print("\n📖 PRUNE DOCUMENTATION")
    print(checkpointer.prune.__doc__)