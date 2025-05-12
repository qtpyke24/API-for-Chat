from flask import jsonify
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, Forbidden, NotFound, ServiceUnavailable

def setup_exception_handler(app):
    """
    Thiết lập xử lý ngoại lệ cho ứng dụng Flask, bao gồm các mã lỗi HTTP cụ thể
    và các ngoại lệ chung.
    """
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return jsonify({
            "error": "Yêu cầu không hợp lệ",
            "message": str(e.description) if e.description else "Dữ liệu đầu vào không đúng định dạng hoặc thiếu thông tin"
        }), 400

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        return jsonify({
            "error": "Không được phép",
            "message": str(e.description) if e.description else "Yêu cầu xác thực, vui lòng cung cấp token hợp lệ"
        }), 401

    @app.errorhandler(Forbidden)
    def handle_forbidden(e):
        return jsonify({
            "error": "Bị cấm",
            "message": str(e.description) if e.description else "Bạn không có quyền truy cập tài nguyên này"
        }), 403

    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return jsonify({
            "error": "Không tìm thấy",
            "message": str(e.description) if e.description else "Tài nguyên yêu cầu không tồn tại"
        }), 404

    @app.errorhandler(ServiceUnavailable)
    def handle_service_unavailable(e):
        return jsonify({
            "error": "Dịch vụ không khả dụng",
            "message": str(e.description) if e.description else "Hệ thống hiện đang bảo trì hoặc gặp sự cố"
        }), 503

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "error": "Lỗi HTTP",
            "message": str(e.description) if e.description else "Đã xảy ra lỗi trong quá trình xử lý yêu cầu",
            "code": e.code
        }), e.code

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        return jsonify({
            "error": "Lỗi server nội bộ",
            "message": str(e) if app.debug else "Đã xảy ra lỗi không mong muốn, vui lòng thử lại sau"
        }), 500
