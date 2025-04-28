from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room
from flasgger import Swagger
import json
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
swagger = Swagger(app)

CHAT_FILE = 'chat_messages.json'
NOTIFICATION_FILE = 'notifications.json'
USER_FILE = 'users.json'
CONTACT_FILE = 'contacts.json'

# Load existing data
def load_json(file_path, default={}):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

messages = load_json(CHAT_FILE)
notifications = load_json(NOTIFICATION_FILE)
users = load_json(USER_FILE)
contacts = load_json(CONTACT_FILE)

# Save data helper
def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)


@app.route('/')
def index():
    return render_template('E:\\PyCharmProjects\\pythonProject\\tkdgtt\\LT 2May\\index2.html')


@app.route('/messages/<room>', methods=['GET'])
def get_messages(room):
    """
    Lấy tất cả tin nhắn của một phòng chat.
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
        description: Tên phòng chat
    responses:
      200:
        description: Danh sách tin nhắn
        schema:
          type: object
          properties:
            room:
              type: string
            messages:
              type: array
              items:
                type: object
                properties:
                  username:
                    type: string
                  message:
                    type: string
    """
    return jsonify({"room": room, "messages": messages.get(room, [])})


@app.route('/messages', methods=['POST'])
def send_message():
    """
    Gửi tin nhắn vào một phòng chat.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            room:
              type: string
            username:
              type: string
            message:
              type: string
    responses:
      200:
        description: Tin nhắn đã gửi thành công
    """
    data = request.json
    room = data.get("room")
    username = data.get("username")
    message = data.get("message")

    if not room or not username or not message:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    if room not in messages:
        messages[room] = []

    messages[room].append({"username": username, "message": message})

    with open(CHAT_FILE, 'w') as file:
        json.dump(messages, file)

    socketio.emit('update_chat', messages[room], room=room)
    return jsonify({"message": "Tin nhắn đã gửi"}), 200


@app.route('/notifications/<username>', methods=['GET'])
def get_notifications(username):
    """
    Lấy danh sách thông báo của một người dùng
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
    responses:
      200:
        description: Danh sách thông báo
    """
    user_notifications = notifications.get(username, [])
    return jsonify({"username": username, "notifications": user_notifications})


@app.route('/notifications', methods=['POST'])
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
    responses:
      200:
        description: Thông báo đã được tạo
    """
    data = request.json
    username = data.get("username")
    message = data.get("message")
    notif_type = data.get("type","info")

    if not username or not message:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    if username not in notifications:
        notifications[username] = []

    notification = {
        "message": message,
        "type": notif_type,
        "timestamp": datetime.now().isoformat()
    }
    notifications[username].append(notification)
    save_json(NOTIFICATION_FILE, notifications)
    socketio.emit('new_notification', notification, room=username)
    return jsonify({"message": "Thông báo đã được tạo"}), 200


# New API: Attachment
@app.route('/messages/<room>/attachment', methods=['POST'])
def upload_attachment():
    """
    Upload file đính kèm cho một phòng chat
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
      - name: username
        in: formData
        type: string
        required: true
      - name: file
        in: formData
        type: file
        required: true
    responses:
      200:
        description: File đã được upload
    """
    if 'file' not in request.files:
        return jsonify({"error": "Không có file"}), 400

    file = request.files['file']
    username = request.form.get('username')
    room = request.path.split('/')[2]

    if not username or not file:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    # Save file
    filename = f"attachments/{room}/{datetime.now().timestamp()}_{file.filename}"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file.save(filename)

    # Add to messages
    if room not in messages:
        messages[room] = []
    message = {
        "username": username,
        "attachment": filename,
        "type": "attachment",
        "timestamp": datetime.now().isoformat()
    }
    messages[room].append(message)
    save_json(CHAT_FILE, messages)
    socketio.emit('update_chat', messages[room], room=room)
    return jsonify({"message": "File đã được upload"}), 200



# New API: Participants
@app.route('/rooms/<room>/participants', methods=['GET'])
def get_participants(room):
    """
    Lấy danh sách người tham gia phòng chat
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
    responses:
      200:
        description: Danh sách người tham gia
    """
    room_users = users.get(room, [])
    return jsonify({"room": room, "participants": room_users})


@app.route('/rooms/<room>/participants', methods=['POST'])
def add_participant(room):
    """
    Thêm người tham gia vào phòng chat
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
    responses:
      200:
        description: Đã thêm người tham gia
    """
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Thiếu username"}), 400

    if room not in users:
        users[room] = []
    if username not in users[room]:
        users[room].append(username)
        save_json(USER_FILE, users)
        socketio.emit('update_participants', users[room], room=room)
    return jsonify({"message": "Đã thêm người tham gia"}), 200


# New API: Group Settings
@app.route('/rooms/<room>/settings', methods=['PUT'])
def update_group_settings(room):
    """
    Cập nhật cài đặt nhóm
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            privacy:
              type: string
    responses:
      200:
        description: Đã cập nhật cài đặt
    """
    data = request.json
    if room not in messages:
        return jsonify({"error": "Phòng không tồn tại"}), 404

    settings = messages[room].get("settings", {})
    settings.update({
        "name": data.get("name", settings.get("name")),
        "description": data.get("description", settings.get("description")),
        "privacy": data.get("privacy", settings.get("privacy"))
    })
    messages[room]["settings"] = settings
    save_json(CHAT_FILE, messages)
    socketio.emit('update_settings', settings, room=room)
    return jsonify({"message": "Đã cập nhật cài đặt"}), 200


# New API: Blocked Users
@app.route('/rooms/<room>/blocked', methods=['POST'])
def block_user(room):
    """
    Chặn một người dùng trong phòng chat
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
    responses:
      200:
        description: Đã chặn người dùng
    """
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Thiếu username"}), 400

    if room not in users:
        users[room] = {"participants": [], "blocked": []}

    if "blocked" not in users[room]:
        users[room]["blocked"] = []

    if username not in users[room]["blocked"]:
        users[room]["blocked"].append(username)
        save_json(USER_FILE, users)
        socketio.emit('update_blocked', users[room]["blocked"], room=room)
    return jsonify({"message": "Đã chặn người dùng"}), 200

@app.route('/messages/<room>/<message_id>/status', methods=['GET'])
def get_message_status(room, message_id):
    """
    Lấy trạng thái chi tiết của một tin nhắn (gửi, nhận, đọc) cho từng người dùng
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
        description: Tên phòng chat
      - name: message_id
        in: path
        type: string
        required: true
        description: ID tin nhắn (timestamp)
    responses:
      200:
        description: Trạng thái tin nhắn
        schema:
          type: object
          properties:
            room:
              type: string
            message_id:
              type: string
            status:
              type: object
              properties:
                sent:
                  type: boolean
                delivered:
                  type: object
                read:
                  type: object
    """
    if room not in messages:
        return jsonify({"error": "Phòng không tồn tại"}), 404

    for msg in messages[room]:
        if msg.get("timestamp") == message_id:
            return jsonify({
                "room": room,
                "message_id": message_id,
                "status": msg.get("status", {"sent": False, "delivered": {}, "read": {}})
            })
    return jsonify({"error": "Không tìm thấy tin nhắn"}), 404

@app.route('/messages/<room>/<message_id>/status', methods=['PUT'])
def update_message_status(room, message_id):
    """
    Cập nhật trạng thái tin nhắn (delivered/read) cho một người dùng
    ---
    parameters:
      - name: room
        in: path
        type: string
        required: true
      - name: message_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            status:
              type: string
              enum: [delivered, read]
    responses:
      200:
        description: Trạng thái đã được cập nhật
    """
    data = request.json
    username = data.get("username")
    status = data.get("status")

    if not username or not status or status not in ["delivered", "read"]:
        return jsonify({"error": "Dữ liệu không hợp lệ"}), 400

    if room not in messages:
        return jsonify({"error": "Phòng không tồn tại"}), 404

    for msg in messages[room]:
        if msg.get("timestamp") == message_id:
            if "status" not in msg:
                msg["status"] = {"sent": True, "delivered": {}, "read": {}}
            msg["status"][status][username] = datetime.now().isoformat()
            save_json(CHAT_FILE, messages)
            socketio.emit('update_status', {
                "message_id": message_id,
                "status": msg["status"]
            }, room=room)
            return jsonify({"message": f"Đã cập nhật trạng thái {status}"}), 200
    return jsonify({"error": "Không tìm thấy tin nhắn"}), 404

# New API: UserContact
@app.route('/contacts/<username>', methods=['GET'])
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
            username:
              type: string
            contacts:
              type: array
              items:
                type: object
                properties:
                  contact_username:
                    type: string
                  nickname:
                    type: string
                  added_at:
                    type: string
    """
    user_contacts = contacts.get(username, [])
    return jsonify({"username": username, "contacts": user_contacts})

@app.route('/contacts', methods=['POST'])
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
    """
    data = request.json
    username = data.get("username")
    contact_username = data.get("contact_username")
    nickname = data.get("nickname", contact_username)

    if not username or not contact_username:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    if username not in contacts:
        contacts[username] = []

    # Kiểm tra xem contact đã tồn tại chưa
    for contact in contacts[username]:
        if contact["contact_username"] == contact_username:
            return jsonify({"error": "Người dùng đã có trong danh bạ"}), 400

    contact_data = {
        "contact_username": contact_username,
        "nickname": nickname,
        "added_at": datetime.now().isoformat()
    }
    contacts[username].append(contact_data)
    save_json(CONTACT_FILE, contacts)
    socketio.emit('update_contacts', contacts[username], room=username)
    return jsonify({"message": "Đã thêm vào danh bạ"}), 200

@app.route('/contacts/<username>/<contact_username>', methods=['PUT'])
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
    """
    data = request.json
    nickname = data.get("nickname")

    if not nickname:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    if username not in contacts:
        return jsonify({"error": "Người dùng không có danh bạ"}), 404

    for contact in contacts[username]:
        if contact["contact_username"] == contact_username:
            contact["nickname"] = nickname
            save_json(CONTACT_FILE, contacts)
            socketio.emit('update_contacts', contacts[username], room=username)
            return jsonify({"message": "Đã cập nhật danh bạ"}), 200
    return jsonify({"error": "Không tìm thấy liên hệ"}), 404

@app.route('/contacts/<username>/<contact_username>', methods=['DELETE'])
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
    """
    if username not in contacts:
        return jsonify({"error": "Người dùng không có danh bạ"}), 404

    for i, contact in enumerate(contacts[username]):
        if contact["contact_username"] == contact_username:
            contacts[username].pop(i)
            save_json(CONTACT_FILE, contacts)
            socketio.emit('update_contacts', contacts[username], room=username)
            return jsonify({"message": "Đã xóa khỏi danh bạ"}), 200
    return jsonify({"error": "Không tìm thấy liên hệ"}), 404

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)

    if room not in messages:
        messages[room] = []

    socketio.emit('update_chat', messages[room], room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
