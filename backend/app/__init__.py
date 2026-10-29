import os
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

    uri = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")

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