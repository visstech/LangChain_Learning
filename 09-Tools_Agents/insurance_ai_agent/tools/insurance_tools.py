from langchain.tools import tool
from database.postgres import PostgreSQL
from services.policy_service import PolicyService
from services.customer_service import CustomerService
from services.claim_service import ClaimService

def create_user_tools(session):
    """
    Create tools restricted to the authenticated user.
    """

    authenticated_user_id = session.get_user_id()

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

            policy = policy_service.get_policy_by_customer(
                authenticated_user_id
            )

            if policy is None:
                return "No policy found for the authenticated customer."

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

    @tool
    def get_my_claims():
        """
        Get all insurance claims belonging to the
        currently authenticated customer.

        This tool never accepts a customer ID.
        """

        db = PostgreSQL()
        db.connect()

        try:
            claim_service = ClaimService(db)

            claims = claim_service.get_claims_by_customer(
                authenticated_user_id
            )

            if not claims:
                return "No claims found for the authenticated customer."

            results = []

            for claim in claims:
                results.append({
                    "claim_id": claim[0],
                    "customer_id": claim[1],
                    "policy_id": claim[2],
                    "incident_date": str(claim[3]),
                    "claim_date": str(claim[4]),
                    "status": claim[5],
                    "amount": str(claim[6]),
                    "reason": claim[7]
                })

            return results

        finally:
            db.close()

    return [
        get_my_policy,
        get_my_claims
    ]