from datetime import datetime

class Message:
    def __init__(self, username, message, room):
        self.username = username
        self.message = message
        self.room = room
        self.timestamp = datetime.now().isoformat()
        self.status = {"sent": True, "delivered": {}, "read": {}}

    def to_dict(self):
        return {
            "username": self.username,
            "message": self.message,
            "timestamp": self.timestamp,
            "status": self.status
        }