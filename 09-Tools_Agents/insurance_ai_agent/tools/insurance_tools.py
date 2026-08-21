from langchain.tools import tool

from database.postgres import PostgreSQL
from services.policy_service import PolicyService
from services.customer_service import CustomerService
from services.claim_service import ClaimService


def create_user_tools(session):
    """
    Create tools restricted to the authenticated user.

    IMPORTANT:
    The authenticated customer ID always comes from
    the Session object.

    The LLM never supplies the customer ID.
    """

    authenticated_user_id = session.get_user_id()

    # =========================================================
    # GET MY POLICY
    # =========================================================

    @tool
    def get_my_policy():
        """
        Get the insurance policy of the currently
        authenticated customer.

        This tool never accepts a customer ID.
        """

        db = PostgreSQL()
        db.connect()

        try:

            policy_service = PolicyService(db)

            policy = (
                policy_service.get_policy_by_customer(
                    authenticated_user_id
                )
            )

            if policy is None:

                return (
                    "No policy found for the "
                    "authenticated customer."
                )

            return {
                "policy_id": policy[0],
                "customer_id": policy[1],
                "policy_type": policy[2],
                "status": policy[3],
                "start_date": str(policy[4]),
                "expiry_date": str(policy[5]),
                "premium": str(policy[6])
            }

        finally:

            db.close()

    # =========================================================
    # GET MY CLAIMS
    # =========================================================

    @tool
    def get_my_claims():
        """
        Get all insurance claims belonging to the
        currently authenticated customer.

        This tool never accepts a customer ID.

        Use this tool when the customer asks about
        their claims in general or asks for their
        current claims.
        """

        db = PostgreSQL()
        db.connect()

        try:

            claim_service = ClaimService(db)

            claims = (
                claim_service.get_claims_by_customer(
                    authenticated_user_id
                )
            )

            if not claims:

                return (
                    "No claims found for the "
                    "authenticated customer."
                )

            results = []

            for claim in claims:

                results.append(
                    {
                        "claim_id": claim[0],
                        "customer_id": claim[1],
                        "policy_id": claim[2],
                        "incident_date": str(
                            claim[3]
                        ),
                        "claim_date": str(
                            claim[4]
                        ),
                        "status": claim[5],
                        "amount": str(
                            claim[6]
                        ),
                        "reason": claim[7]
                    }
                )

            return results

        finally:

            db.close()

    # =========================================================
    # GET MY CLAIM STATUS
    # =========================================================

    @tool
    def get_my_claim_status(claim_id: str):
        """
        Get the status of a specific insurance claim
        belonging to the currently authenticated customer.

        Use this tool when the customer provides a
        specific claim ID.

        Example:

            "What is the status of CLM001?"

        The customer ID must never be supplied by the LLM.

        The authenticated customer's ID is obtained
        from the Session.
        """

        db = PostgreSQL()
        db.connect()

        try:

            claim_service = ClaimService(db)

            claim = (
                claim_service.get_claim_by_id_and_customer(
                    claim_id,
                    authenticated_user_id
                )
            )

            if claim is None:

                return (
                    "Claim not found for the "
                    "authenticated customer."
                )

            return {
                "claim_id": claim["claim_id"],
                "customer_id": claim["customer_id"],
                "policy_id": claim["policy_id"],
                "incident_date": claim["incident_date"],
                "claim_date": claim["claim_date"],
                "status": claim["status"],
                "amount": claim["amount"],
                "reason": claim["reason"]
            }

        finally:

            db.close()

    # =========================================================
    # RETURN TOOLS
    # =========================================================

    return [
        get_my_policy,
        get_my_claims,
        get_my_claim_status
    ]