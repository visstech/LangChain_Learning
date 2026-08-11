class Session:

    def __init__(self, user_id: str):
        self.user_id = user_id

    def get_user_id(self) -> str:
        return self.user_id
