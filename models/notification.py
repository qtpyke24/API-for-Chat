from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), ForeignKey('users.username'), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), default='info')
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "message": self.message,
            "type": self.type,
            "timestamp": self.timestamp.isoformat()
        }