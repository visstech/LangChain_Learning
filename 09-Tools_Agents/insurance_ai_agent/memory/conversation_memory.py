"""
Persistent Conversation Memory.

Stores and retrieves customer conversation history
from PostgreSQL.
"""

from database.postgres import PostgreSQL


class ConversationMemory:
    """
    PostgreSQL-backed conversation memory.

    Conversation history is always isolated by
    authenticated customer_id.
    """

    def __init__(self, customer_id):

        self.customer_id = customer_id

    def save_message(self, role, content):
        """
        Save one conversation message.
        """

        db = PostgreSQL()

        try:

            connection = db.connect()

            cursor = connection.cursor()

            query = """
                INSERT INTO conversation_messages
                (
                    customer_id,
                    role,
                    content
                )
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    self.customer_id,
                    role,
                    content
                )
            )

            connection.commit()

            cursor.close()

        finally:

            db.close()

    def load_messages(self):
        """
        Load conversation history for the
        authenticated customer only.
        """

        db = PostgreSQL()

        try:

            connection = db.connect()

            cursor = connection.cursor()

            query = """
                SELECT
                    role,
                    content
                FROM conversation_messages
                WHERE customer_id = %s
                ORDER BY created_at ASC, id ASC
            """

            cursor.execute(
                query,
                (self.customer_id,)
            )

            rows = cursor.fetchall()

            cursor.close()

            return rows

        finally:

            db.close()

    def clear_messages(self):
        """
        Delete conversation history for the
        authenticated customer only.
        """

        db = PostgreSQL()

        try:

            connection = db.connect()

            cursor = connection.cursor()

            query = """
                DELETE FROM conversation_messages
                WHERE customer_id = %s
            """

            cursor.execute(
                query,
                (self.customer_id,)
            )

            connection.commit()

            cursor.close()

        finally:

            db.close()
            
    def load_recent_messages(self, limit=6):

        db = PostgreSQL()

        try:

            connection = db.connect()

            cursor = connection.cursor()

            query = """
                SELECT role, content
                FROM conversation_messages
                WHERE customer_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """

            cursor.execute(
                query,
                (
                    self.customer_id,
                    limit
                )
            )

            rows = cursor.fetchall()

            cursor.close()

            # Database returns newest first.
            # Reverse so conversation order is preserved.
            rows.reverse()

            return rows

        finally:

            db.close()        
    
    def load_recent_conversation_history(self):

        rows = self.conversation_memory.load_recent_messages(
            limit=6
        )

        history = []

        for role, content in rows:

            if role == "user":

                history.append(
                    HumanMessage(
                        content=content
                    )
                )

            elif role == "assistant":

                history.append(
                    AIMessage(
                        content=content
                    )
                )

        print(
            "\nRecent conversation messages:",
            len(history)
        )

        return history