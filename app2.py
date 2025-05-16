from flask import Flask
from flask_socketio import SocketIO, join_room
from flasgger import Swagger
from middleware import setup_exception_handler
from routes import messages_bp, contacts_bp, notifications_bp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")
swagger = Swagger(app)

# Khởi tạo SQLAlchemy
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data/chat.db')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Đăng ký blueprints
app.register_blueprint(messages_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(notifications_bp)

# Thiết lập xử lý ngoại lệ
setup_exception_handler(app)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)

    session = Session()
    try:
        from models import Message
        messages = session.query(Message).filter_by(room=room).all()
        socketio.emit('update_chat', [msg.to_dict() for msg in messages], room=room)
    finally:
        session.close()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
