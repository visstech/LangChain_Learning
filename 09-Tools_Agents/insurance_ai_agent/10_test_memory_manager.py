"""
=====================================================

Topic:
Testing PostgreSQL MemoryManager

=====================================================
"""

from memory.memory_manager import MemoryManager


memory = MemoryManager(

    host="localhost",

    port=5432,

    database="insurance_ai",

    user="postgres",

    password="postgres123"

)


# Save memory

memory.save_memory(

    user_id="CUST001",

    memory_key="customer_id",

    memory_value="CUST001",

    memory_type="customer",

    importance=10

)


memory.save_memory(

    user_id="CUST001",

    memory_key="name",

    memory_value="Senthil",

    memory_type="customer",

    importance=8

)


memory.save_memory(

    user_id="CUST001",

    memory_key="policy",

    memory_value="Motor Insurance",

    memory_type="policy",

    importance=8

)


# Get one memory

customer_id = memory.get_memory(

    "CUST001",

    "customer_id"

)

print(
    "\nCustomer ID:",
    customer_id
)


# Get all memories

print(
    "\nAll Memories:"
)

all_memories = memory.get_all_memories(
    "CUST001"
)

for item in all_memories:

    print(item)


memory.close()