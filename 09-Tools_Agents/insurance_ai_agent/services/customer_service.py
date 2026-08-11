"""
Customer service module.

Contains business operations related to customers.
"""

class CustomerService:
    """
    Provides customer-related database operations.
    """

    def __init__(self, db):
        """
        Initialize the customer service.

        Args:
            db: PostgreSQL database connection object.
        """

        self.db = db

    def get_customer(self, customer_id):
        """
        Retrieve customer information by customer ID.

        Args:
            customer_id: Unique customer identifier.

        Returns:
            Customer record if found, otherwise None.
        """

        query = """
            SELECT
                customer_id,
                name,
                email,
                phone
            FROM customers
            WHERE customer_id = %s
        """

        cursor = self.db.connection.cursor()

        cursor.execute(query, (customer_id,))

        result = cursor.fetchone()

        cursor.close()

        return result