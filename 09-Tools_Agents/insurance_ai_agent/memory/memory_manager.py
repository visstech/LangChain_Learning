"""
=====================================================

Topic:
PostgreSQL Memory Manager

Concepts Covered:

- PostgreSQL
- psycopg
- Database Connection
- Persistent Memory
- CRUD Operations
- Memory Manager

Learning Goal:

Build a reusable MemoryManager class
that allows our AI Agent to store and
retrieve long-term memories.

=====================================================
"""

import psycopg


class MemoryManager:

    def __init__(
        self,
        host="localhost",
        port=5432,
        database="insurance_ai",
        user="postgres",
        password=""
    ):

        self.connection = psycopg.connect(

            host=host,

            port=port,

            dbname=database,

            user=user,

            password=password

        )

        print(
            "PostgreSQL connected successfully."
        )

        self.create_table()


    # =================================================
    # Create Memory Table
    # =================================================

    def create_table(self):

        query = """

        CREATE TABLE IF NOT EXISTS memories (

            id SERIAL PRIMARY KEY,

            user_id VARCHAR(100) NOT NULL,

            memory_key VARCHAR(100) NOT NULL,

            memory_value TEXT NOT NULL,

            memory_type VARCHAR(50),

            importance INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id, memory_key)

        );

        """

        with self.connection.cursor() as cursor:

            cursor.execute(query)

        self.connection.commit()

        print(
            "Memory table ready."
        )


    # =================================================
    # Save Memory
    # =================================================

    def save_memory(
        self,
        user_id,
        memory_key,
        memory_value,
        memory_type="general",
        importance=1
    ):

        query = """

        INSERT INTO memories (

            user_id,
            memory_key,
            memory_value,
            memory_type,
            importance

        )

        VALUES (%s, %s, %s, %s, %s)

        ON CONFLICT (user_id, memory_key)

        DO UPDATE SET

            memory_value = EXCLUDED.memory_value,

            memory_type = EXCLUDED.memory_type,

            importance = EXCLUDED.importance,

            updated_at = CURRENT_TIMESTAMP;

        """

        with self.connection.cursor() as cursor:

            cursor.execute(

                query,

                (
                    user_id,
                    memory_key,
                    memory_value,
                    memory_type,
                    importance
                )

            )

        self.connection.commit()

        print(
            "Memory saved:",
            memory_key,
            "=",
            memory_value
        )


    # =================================================
    # Get Memory
    # =================================================

    def get_memory(
        self,
        user_id,
        memory_key
    ):

        query = """

        SELECT memory_value

        FROM memories

        WHERE user_id = %s

        AND memory_key = %s;

        """

        with self.connection.cursor() as cursor:

            cursor.execute(

                query,

                (
                    user_id,
                    memory_key
                )

            )

            result = cursor.fetchone()


        if result:

            return result[0]

        return None


    # =================================================
    # Get All Memories
    # =================================================

    def get_all_memories(
        self,
        user_id
    ):

        query = """

        SELECT

            memory_key,
            memory_value,
            memory_type,
            importance

        FROM memories

        WHERE user_id = %s

        ORDER BY updated_at DESC;

        """

        with self.connection.cursor() as cursor:

            cursor.execute(

                query,

                (user_id,)

            )

            return cursor.fetchall()


    # =================================================
    # Delete Memory
    # =================================================

    def delete_memory(
        self,
        user_id,
        memory_key
    ):

        query = """

        DELETE FROM memories

        WHERE user_id = %s

        AND memory_key = %s;

        """

        with self.connection.cursor() as cursor:

            cursor.execute(

                query,

                (
                    user_id,
                    memory_key
                )

            )

        self.connection.commit()


    # =================================================
    # Close Connection
    # =================================================

    def close(self):

        self.connection.close()

        print(
            "PostgreSQL connection closed."
        )