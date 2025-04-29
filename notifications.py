from flask import Blueprint, jsonify, request
from middleware.auth import require_auth
from middleware.validation import validate_model
import json
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)
NOTIFICATION_FILE = 'data/notifications.json'

def load_notifications():
    try:
        with open(NOTIFICATION_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_notifications(notifications):
    with open(NOTIFICATION_FILE, 'w') as f:
        json.dump(notifications, f)

# Schema cho validation
SCHEMAS = {
    'notification': {
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'minLength': 1},
            'message': {'type': 'string', 'minLength': 1},
            'type': {'type': 'string', 'enum': ['info', 'warning', 'error']}
        },
        'required': ['username', 'message']
    }
}

@notifications_bp.route('/notifications/<username>', methods=['GET'])
@require_auth
def get_notifications(username):
    """
    Lấy danh sách thông báo của một người dùng
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: Tên người dùng
    responses:
      200:
        description: Danh sách thông báo
        schema:
          type: object
          properties:
            username:
              type: string
            notifications:
              type: array
              items:
                type: object
                properties:
                  message:
                    type: string
                  type:
                    type: string
                  timestamp:
                    type: string
    """
    notifications = load_notifications()
    return jsonify({"username": username, "notifications": notifications.get(username, [])})

@notifications_bp.route('/notifications', methods=['POST'])
@require_auth
@validate_model('notification')
def create_notification():
    """
    Tạo một thông báo mới
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            message:
              type: string
            type:
              type: string
              enum: [info, warning, error]
    responses:
      200:
        description: Thông báo đã được tạo
    """
    data = request.json
    username = data.get("username")
    message = data.get("message")
    notif_type = data.get("type", "info")

    notifications = load_notifications()
    if username not in notifications:
        notifications[username] = []

    notification = {
        "message": message,
        "type": notif_type,
        "timestamp": datetime.now().isoformat()
    }
    notifications[username].append(notification)
    save_notifications(notifications)

    from app import socketio
    socketio.emit('new_notification', notification, room=username)
    return jsonify({"message": "Thông báo đã được tạo"}), 200

@notifications_bp.route('/notifications/<username>/<notification_id>', methods=['DELETE'])
@require_auth
def delete_notification(username, notification_id):
    """
    Xóa một thông báo của người dùng
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: Tên người dùng
      - name: notification_id
        in: path
        type: string
        required: true
        description: ID thông báo (timestamp)
    responses:
      200:
        description: Thông báo đã được xóa
      404:
        description: Không tìm thấy thông báo
    """
    notifications = load_notifications()
    if username not in notifications:
        return jsonify({"error": "Không tìm thấy danh sách thông báo"}), 404

    for i, notif in enumerate(notifications[username]):
        if notif["timestamp"] == notification_id:
            notifications[username].pop(i)
            save_notifications(notifications)
            from app import socketio
            socketio.emit('update_notifications', notifications[username], room=username)
            return jsonify({"message": "Thông báo đã được xóa"}), 200
    return jsonify({"error": "Không tìm thấy thông báo"}), 404