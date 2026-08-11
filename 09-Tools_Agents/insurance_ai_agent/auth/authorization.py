class Authorization:

    @staticmethod
    def check_access(
        authenticated_user_id: str,
        resource_owner_id: str
    ) -> bool:

        return (
            authenticated_user_id.upper()
            == resource_owner_id.upper()
        )