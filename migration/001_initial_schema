import json
import os
from datetime import datetime

CHAT_FILE = 'data/chat_messages.json'
CONTACT_FILE = 'data/contacts.json'
USER_FILE = 'data/users.json'
NOTIFICATION_FILE = 'data/notifications.json'

def init_schema():
    """Khởi tạo schema ban đầu cho các file JSON"""
    # Đảm bảo thư mục data tồn tại
    os.makedirs('data', exist_ok=True)

    # Schema cho chat_messages.json
    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, 'w') as f:
            json.dump({}, f)

    # Schema cho contacts.json
    if not os.path.exists(CONTACT_FILE):
        with open(CONTACT_FILE, 'w') as f:
            json.dump({}, f)

    # Schema cho users.json
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({}, f)

    # Schema cho notifications.json
    if not os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, 'w') as f:
            json.dump({}, f)

def run_migration():
    print("Chạy migration 001_initial_schema...")
    init_schema()
    print("Hoàn thành migration.")

if __name__ == '__main__':
    run_migration()
