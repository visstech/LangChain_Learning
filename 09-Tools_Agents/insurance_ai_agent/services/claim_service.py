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

    # =========================================================
    # Get all claims for authenticated customer
    # =========================================================

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

        try:

            cursor.execute(
                query,
                (customer_id,)
            )

            results = cursor.fetchall()

            return results

        finally:

            cursor.close()

    # =========================================================
    # Get ONE claim for authenticated customer
    # =========================================================

    def get_claim_by_id_and_customer(
        self,
        claim_id,
        customer_id
    ):
        """
        Retrieve one specific claim belonging
        to the authenticated customer.

        Security:
            The claim_id AND customer_id must match.

        Args:
            claim_id:
                Unique claim identifier.

            customer_id:
                Authenticated customer identifier.

        Returns:
            Claim record as a dictionary,
            or None if the claim does not belong
            to the customer.
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
            WHERE claim_id = %s
              AND customer_id = %s
        """

        cursor = self.db.connection.cursor()

        try:

            cursor.execute(
                query,
                (
                    claim_id,
                    customer_id
                )
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "claim_id": row[0],
                "customer_id": row[1],
                "policy_id": row[2],
                "incident_date": str(row[3]),
                "claim_date": str(row[4]),
                "status": row[5],
                "amount": str(row[6]),
                "reason": row[7]
            }

        finally:

            cursor.close()