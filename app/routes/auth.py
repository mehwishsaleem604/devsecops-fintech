import time
import logging
import jwt
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.main import db, token_required
from app.models import User
from app.metrics import LOGIN_FAILURES
from app.config import JWT_SECRET, JWT_ALGO, JWT_EXP_SECS

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/v1/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "password", "email")):
        return jsonify({"error": "Missing required fields"}), 400
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409
    user = User(
        username=data["username"],
        password_hash=generate_password_hash(data["password"]),
        email=data["email"],
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "user_id": user.id}), 201

@auth_bp.route("/api/v1/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    logger.debug("Login attempt: username=%s password=%s", username, password)
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        LOGIN_FAILURES.inc()
        return jsonify({"error": "Invalid credentials"}), 401
    token = jwt.encode(
        {"user_id": user.id, "role": user.role, "exp": time.time() + JWT_EXP_SECS},
        JWT_SECRET,
        algorithm=JWT_ALGO,
    )
    return jsonify({"token": token, "user_id": user.id})