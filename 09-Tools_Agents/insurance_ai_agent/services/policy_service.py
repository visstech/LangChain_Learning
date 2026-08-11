"""
Policy service module.

Contains business operations related to insurance policies.
"""


class PolicyService:
    """
    Provides policy-related database operations.
    """

    def __init__(self, db):
        """
        Initialize the policy service.

        Args:
            db: PostgreSQL database connection object.
        """

        self.db = db

    def get_policy_by_customer(self, customer_id):
        """
        Retrieve the policy belonging to a customer.

        Args:
            customer_id: Unique customer identifier.

        Returns:
            Policy record if found, otherwise None.
        """

        query = """
            SELECT
                policy_id,
                customer_id,
                policy_type,
                status,
                start_date,
                expiry_date,
                premium
            FROM policies
            WHERE customer_id = %s
        """

        cursor = self.db.connection.cursor()

        cursor.execute(query, (customer_id,))

        result = cursor.fetchone()

        cursor.close()

        return result