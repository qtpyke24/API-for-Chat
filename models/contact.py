from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), ForeignKey('users.username'), nullable=False)
    contact_username = Column(String(50), ForeignKey('users.username'), nullable=False)
    nickname = Column(String(100))
    added_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "contact_username": self.contact_username,
            "nickname": self.nickname,
            "added_at": self.added_at.isoformat()
        }
