from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
    app.config["JWT_SECRET_KEY"] = "change-me"
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    with app.app_context():
        from . import models
        db.create_all()
        from .auth import auth_bp
        app.register_blueprint(auth_bp)
        from .events import events_bp
        app.register_blueprint(events_bp)
        from . import sockets
    return app