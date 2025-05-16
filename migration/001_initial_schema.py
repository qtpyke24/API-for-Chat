from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Định nghĩa cơ sở dữ liệu
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../data/chat.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Định nghĩa các bảng
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    room = Column(String(50), nullable=False)
    username = Column(String(50), ForeignKey('users.username'), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Text, default='{"sent": true, "delivered": {}, "read": {}}')

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), ForeignKey('users.username'), nullable=False)
    contact_username = Column(String(50), ForeignKey('users.username'), nullable=False)
    nickname = Column(String(100))
    added_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), ForeignKey('users.username'), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), default='info')
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_schema():
    """Tạo các bảng trong cơ sở dữ liệu"""
    os.makedirs(os.path.join(BASE_DIR, '../data'), exist_ok=True)
    Base.metadata.create_all(engine)

def run_migration():
    print("Chạy migration 001_initial_schema...")
    init_schema()
    print("Hoàn thành migration.")

if __name__ == '__main__':
    run_migration()
