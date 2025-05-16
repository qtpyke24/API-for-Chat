from flask import Blueprint, jsonify, request
from middleware.auth import require_auth
from middleware.validation import validate_model
from models import Contact, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

contacts_bp = Blueprint('contacts', __name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../data/chat.db')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Schema cho validation
SCHEMAS = {
    'contact': {
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'minLength': 1},
            'contact_username': {'type': 'string', 'minLength': 1},
            'nickname': {'type': 'string'}
        },
        'required': ['username', 'contact_username']
    },
    'update_contact': {
        'type': 'object',
        'properties': {
            'nickname': {'type': 'string', 'minLength': 1}
        },
        'required': ['nickname']
    }
}

@contacts_bp.route('/contacts/<username>', methods=['GET'])
@require_auth
def get_contacts(username):
    """
    Lấy danh sách danh bạ của một người dùng
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: Tên người dùng
    responses:
      200:
        description: Danh sách danh bạ
        schema:
          type: object
          properties:
            usernameper:
              type: string
            username:
              type: string
            contacts:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  username:
                    type: string
                  contact_username:
                    type: string
                  nickname:
                    type: string
                  added_at:
                    type: string
    """
    session = Session()
    try:
        contacts = session.query(Contact).filter_by(username=username).all()
        return jsonify({"username": username, "contacts": [contact.to_dict() for contact in contacts]})
    finally:
        session.close()

@contacts_bp.route('/contacts', methods=['POST'])
@require_auth
@validate_model('contact')
def add_contact():
    """
    Thêm một người dùng vào danh bạ
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
            contact_username:
              type: string
            nickname:
              type: string
    responses:
      200:
        description: Đã thêm vào danh bạ
      404:
        description: Người dùng không tồn tại
      400:
        description: Người dùng đã có trong danh bạ
    """
    data = request.json
    username = data.get("username")
    contact_username = data.get("contact_username")
    nickname = data.get("nickname", contact_username)

    session = Session()
    try:
        # Kiểm tra user và contact user tồn tại
        user = session.query(User).filter_by(username=username).first()
        contact_user = session.query(User).filter_by(username=contact_username).first()
        if not user or not contact_user:
            return jsonify({"error": "Người dùng hoặc liên hệ không tồn tại"}), 404

        # Kiểm tra xem contact đã tồn tại chưa
        existing_contact = session.query(Contact).filter_by(
            username=username, contact_username=contact_username
        ).first()
        if existing_contact:
            return jsonify({"error": "Người dùng đã có trong danh bạ"}), 400

        contact = Contact(username=username, contact_username=contact_username, nickname=nickname)
        session.add(contact)
        session.commit()

        from app import socketio
        contacts = session.query(Contact).filter_by(username=username).all()
        socketio.emit('update_contacts', [c.to_dict() for c in contacts], room=username)
        return jsonify({"message": "Đã thêm vào danh bạ"}), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@contacts_bp.route('/contacts/<username>/<contact_username>', methods=['PUT'])
@require_auth
@validate_model('update_contact')
def update_contact(username, contact_username):
    """
    Cập nhật thông tin liên hệ trong danh bạ
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
      - name: contact_username
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nickname:
              type: string
    responses:
      200:
        description: Đã cập nhật danh bạ
      404:
        description: Không tìm thấy liên hệ
    """
    data = request.json
    nickname = data.get("nickname")

    session = Session()
    try:
        contact = session.query(Contact).filter_by(
            username=username, contact_username=contact_username
        ).first()
        if not contact:
            return jsonify({"error": "Không tìm thấy liên hệ"}), 404

        contact.nickname = nickname
        session.commit()

        from app import socketio
        contacts = session.query(Contact).filter_by(username=username).all()
        socketio.emit('update_contacts', [c.to_dict() for c in contacts], room=username)
        return jsonify({"message": "Đã cập nhật danh bạ"}), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@contacts_bp.route('/contacts/<username>/<contact_username>', methods=['DELETE'])
@require_auth
def remove_contact(username, contact_username):
    """
    Xóa một người dùng khỏi danh bạ
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
      - name: contact_username
        in: path
        type: string
        required: true
    responses:
      200:
        description: Đã xóa khỏi danh bạ
      404:
        description: Không tìm thấy liên hệ
    """
    session = Session()
    try:
        contact = session.query(Contact).filter_by(
            username=username, contact_username=contact_username
        ).first()
        if not contact:
            return jsonify({"error": "Không tìm thấy liên hệ"}), 404

        session.delete(contact)
        session.commit()

        from app import socketio
        contacts = session.query(Contact).filter_by(username=username).all()
        socketio.emit('update_contacts', [c.to_dict() for c in contacts], room=username)
        return jsonify({"message": "Đã xóa khỏi danh bạ"}), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()