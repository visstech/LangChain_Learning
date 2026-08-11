"""
Persistent Conversation Summary.

Stores one summarized conversation context
for each authenticated customer.
"""

from database.postgres import PostgreSQL


class ConversationSummary:

    def __init__(self, customer_id):

        self.customer_id = customer_id

    def get_summary(self):

        db = PostgreSQL()

        try:

            connection = db.connect()

            cursor = connection.cursor()

            query = """
                SELECT summary
                FROM conversation_summaries
                WHERE customer_id = %s
            """

            cursor.execute(
                query,
                (self.customer_id,)
            )

            row = cursor.fetchone()

            cursor.close()

            if row:
                return row[0]

            return None

        finally:

            db.close()

    def save_summary(self, summary):

        db = PostgreSQL()

        try:

            connection = db.connect()

            cursor = connection.cursor()

            query = """
                INSERT INTO conversation_summaries
                (
                    customer_id,
                    summary,
                    updated_at
                )
                VALUES (%s, %s, CURRENT_TIMESTAMP)

                ON CONFLICT (customer_id)
                DO UPDATE SET
                    summary = EXCLUDED.summary,
                    updated_at = CURRENT_TIMESTAMP
            """

            cursor.execute(
                query,
                (
                    self.customer_id,
                    summary
                )
            )

            connection.commit()

            cursor.close()

        finally:

            db.close()