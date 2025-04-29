from flask import jsonify
from werkzeug.exceptions import HTTPException

def setup_exception_handler(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({"error": e.description}), e.code
        return jsonify({"error": "Lỗi server nội bộ", "message": str(e)}), 500