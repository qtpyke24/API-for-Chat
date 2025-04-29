from flask import jsonify, request
from functools import wraps
from jsonschema import validate, ValidationError

# Định nghĩa schema cho các model
SCHEMAS = {
    'message': {
        'type': 'object',
        'properties': {
            'room': {'type': 'string', 'minLength': 1},
            'username': {'type': 'string', 'minLength': 1},
            'message': {'type': 'string', 'minLength': 1}
        },
        'required': ['room', 'username', 'message']
    },
    'contact': {
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'minLength': 1},
            'contact_username': {'type': 'string', 'minLength': 1},
            'nickname': {'type': 'string'}
        },
        'required': ['username', 'contact_username']
    }
}

def validate_model(model_name):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                validate(instance=request.json, schema=SCHEMAS[model_name])
            except ValidationError as e:
                return jsonify({"error": "Dữ liệu không hợp lệ", "message": str(e)}), 400
            return f(*args, **kwargs)
        return decorated
    return decorator