"""
Claim service module.

Contains business operations related to insurance claims.
"""


class ClaimService:
    """
    Provides claim-related database operations.
    """

    def __init__(self, db):
        """
        Initialize the claim service.

        Args:
            db: PostgreSQL database connection object.
        """

        self.db = db

    def get_claims_by_customer(self, customer_id):
        """
        Retrieve all claims belonging to a customer.

        Args:
            customer_id:
                Unique customer identifier.

        Returns:
            List of claim records.
        """

        query = """
            SELECT
                claim_id,
                customer_id,
                policy_id,
                incident_date,
                claim_date,
                status,
                amount,
                reason
            FROM claims
            WHERE customer_id = %s
            ORDER BY claim_date DESC
        """

        cursor = self.db.connection.cursor()

        cursor.execute(query, (customer_id,))

        results = cursor.fetchall()

        cursor.close()

        return results