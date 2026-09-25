from langgraph.checkpoint.postgres import PostgresSaver


DB_URI = (
    "postgresql://postgres:postgres123"
    "@localhost:5432/langgraph_hitl"
)


with PostgresSaver.from_conn_string(DB_URI) as checkpointer:

    checkpointer.setup()

    print("\n📋 PostgresSaver methods:")
    print("=" * 60)

    methods = [
        method
        for method in dir(checkpointer)
        if not method.startswith("_")
    ]

    for method in methods:
        print(method)