from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "participant")

    if not all([name, email, password]):
        return jsonify(error="name, email, password required"), 400
    if role not in ("participant", "organizer"):
        role = "participant"  # admin-ஐ DB-ல manual-ஆ மட்டும் set பண்ணலாம்
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered"), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(message="Registered"), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify(error="Invalid email or password"), 401

    token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role}
    )
    return jsonify(
        token=token,
        user={"id": user.id, "name": user.name, "email": user.email, "role": user.role},
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    return jsonify(id=user.id, name=user.name, email=user.email, role=user.role)