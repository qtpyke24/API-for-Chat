from flask import Blueprint, jsonify, request
from middleware.auth import require_auth, require_room_access
from middleware.validation import validate_model
from models import Message, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

messages_bp = Blueprint('messages', __name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../data/chat.db')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@messages_bp.route('/messages/<room>', methods=['GET'])
@require_auth
@require_room_access
def get_messages(room):
    session = Session()
    try:
        messages = session.query(Message).filter_by(room=room).all()
        return jsonify({"room": room, "messages": [msg.to_dict() for msg in messages]})
    finally:
        session.close()

@messages_bp.route('/messages', methods=['POST'])
@require_auth
@validate_model('message')
def send_message():
    data = request.json
    room = data.get("room")
    username = data.get("username")
    message_text = data.get("message")

    session = Session()
    try:
        # Kiểm tra user tồn tại
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Người dùng không tồn tại"}), 404

        message = Message(room=room, username=username, message=message_text)
        session.add(message)
        session.commit()

        from app import socketio
        socketio.emit('update_chat', message.to_dict(), room=room)
        return jsonify({"message": "Tin nhắn đã gửi"}), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()