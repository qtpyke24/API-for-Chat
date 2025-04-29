from datetime import datetime

class Contact:
    def __init__(self, username, contact_username, nickname=None):
        self.username = username
        self.contact_username = contact_username
        self.nickname = nickname or contact_username
        self.added_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "contact_username": self.contact_username,
            "nickname": self.nickname,
            "added_at": self.added_at
        }