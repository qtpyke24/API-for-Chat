import json
from flask import request, jsonify
import jwt
from functools import wraps
import os

SECRET_KEY = os.getenv('JWT_SECRET', 'your-secret-key')


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Thiếu token xác thực"}), 401

        try:
            token = token.replace("Bearer ", "")
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token đã hết hạn"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token không hợp lệ"}), 401

        return f(*args, **kwargs)

    return decorated


def require_room_access(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        room = kwargs.get('room')
        username = request.user.get('username')

        # Giả sử users.json chứa thông tin phòng mà người dùng có quyền truy cập
        with open('data/users.json', 'r') as f:
            users = json.load(f)

        if room not in users.get(username, {}).get('rooms', []):
            return jsonify({"error": "Không có quyền truy cập phòng này"}), 403

        return f(*args, **kwargs)

    return decorated