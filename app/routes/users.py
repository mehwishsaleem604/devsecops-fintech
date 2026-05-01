
import sqlite3
import logging
from flask import Blueprint, request, jsonify, g
from app.models import User
from app import token_required

logger = logging.getLogger(__name__)
users_bp = Blueprint("users", __name__)

@users_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
@token_required
def get_user(user_id):
    # VULNERABILITY V4 — IDOR: no ownership check
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@users_bp.route("/api/v1/users/search", methods=["GET"])
@token_required
def search_users():
    # VULNERABILITY V1 — SQL Injection
    q = request.args.get("q", "")
    raw_sql = f"SELECT id, username, email, balance FROM users WHERE username LIKE '%{q}%'"
    logger.warning("Executing raw SQL: %s", raw_sql)
    conn = sqlite3.connect("instance/fintech.db")
    cursor = conn.execute(raw_sql)
    rows = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"results": rows, "count": len(rows)})
