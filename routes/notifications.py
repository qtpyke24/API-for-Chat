from flask import Blueprint, jsonify, request
from middleware.auth import require_auth
from middleware.validation import validate_model
from models import Notification, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

notifications_bp = Blueprint('notifications', __name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../data/chat.db')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

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
    session = Session()
    try:
        notifications = session.query(Notification).filter_by(username=username).all()
        return jsonify({"username": username, "notifications": [notif.to_dict() for notif in notifications]})
    finally:
        session.close()

@notifications_bp.route('/notifications', methods=['POST'])
@require_auth
@validate_model('notification')
def create_notification():
    data = request.json
    username = data.get("username")
    message = data.get("message")
    notif_type = data.get("type", "info")

    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Người dùng không tồn tại"}), 404

        notification = Notification(username=username, message=message, type=notif_type)
        session.add(notification)
        session.commit()

        from app import socketio
        socketio.emit('new_notification', notification.to_dict(), room=username)
        return jsonify({"message": "Thông báo đã được tạo"}), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@notifications_bp.route('/notifications/<username>/<notification_id>', methods=['DELETE'])
@require_auth
def delete_notification(username, notification_id):
    session = Session()
    try:
        notification = session.query(Notification).filter_by(username=username, id=notification_id).first()
        if not notification:
            return jsonify({"error": "Không tìm thấy thông báo"}), 404

        session.delete(notification)
        session.commit()

        from app import socketio
        notifications = session.query(Notification).filter_by(username=username).all()
        socketio.emit('update_notifications', [notif.to_dict() for notif in notifications], room=username)
        return jsonify({"message": "Thông báo đã được xóa"}), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()