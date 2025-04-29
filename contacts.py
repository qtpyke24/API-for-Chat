from flask import Blueprint, jsonify, request
from middleware.auth import require_auth
from middleware.validation import validate_model
from models.contact import Contact
import json

contacts_bp = Blueprint('contacts', __name__)
CONTACT_FILE = 'data/contacts.json'

def load_contacts():
    try:
        with open(CONTACT_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_contacts(contacts):
    with open(CONTACT_FILE, 'w') as f:
        json.dump(contacts, f)

@contacts_bp.route('/contacts/<username>', methods=['GET'])
@require_auth
def get_contacts(username):
    contacts = load_contacts()
    return jsonify({"username": username, "contacts": contacts.get(username, [])})

@contacts_bp.route('/contacts', methods=['POST'])
@require_auth
@validate_model('contact')
def add_contact():
    data = request.json
    username = data.get("username")
    contact_username = data.get("contact_username")
    nickname = data.get("nickname", contact_username)

    contacts = load_contacts()
    if username not in contacts:
        contacts[username] = []

    for contact in contacts[username]:
        if contact["contact_username"] == contact_username:
            return jsonify({"error": "Người dùng đã có trong danh bạ"}), 400

    contact = Contact(username, contact_username, nickname)
    contacts[username].append(contact.to_dict())
    save_contacts(contacts)

    from app import socketio
    socketio.emit('update_contacts', contacts[username], room=username)
    return jsonify({"message": "Đã thêm vào danh bạ"}), 200