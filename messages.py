from flask import Blueprint, jsonify, request
from middleware.auth import require_auth, require_room_access
from middleware.validation import validate_model
from models.message import Message
import json

messages_bp = Blueprint('messages', __name__)
CHAT_FILE = 'data/chat_messages.json'

def load_messages():
    try:
        with open(CHAT_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_messages(messages):
    with open(CHAT_FILE, 'w') as f:
        json.dump(messages, f)

@messages_bp.route('/messages/<room>', methods=['GET'])
@require_auth
@require_room_access
def get_messages(room):
    messages = load_messages()
    return jsonify({"room": room, "messages": messages.get(room, [])})

@messages_bp.route('/messages', methods=['POST'])
@require_auth
@validate_model('message')
def send_message():
    data = request.json
    room = data.get("room")
    username = data.get("username")
    message_text = data.get("message")

    messages = load_messages()
    if room not in messages:
        messages[room] = []

    message = Message(username, message_text, room)
    messages[room].append(message.to_dict())
    save_messages(messages)

    # Giả sử socketio được inject từ app
    from app import socketio
    socketio.emit('update_chat', messages[room], room=room)
    return jsonify({"message": "Tin nhắn đã gửi"}), 200