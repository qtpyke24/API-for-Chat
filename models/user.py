class User:
    def __init__(self, username, rooms=None):
        self.username = username
        self.rooms = rooms or []

    def to_dict(self):
        return {
            "username": self.username,
            "rooms": self.rooms
        }