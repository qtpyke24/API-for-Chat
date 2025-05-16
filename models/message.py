from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    room = Column(String(50), nullable=False)
    username = Column(String(50), ForeignKey('users.username'), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Text, default='{"sent": true, "delivered": {}, "read": {}}')

    def to_dict(self):
        return {
            "id": self.id,
            "room": self.room,
            "username": self.username,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }
