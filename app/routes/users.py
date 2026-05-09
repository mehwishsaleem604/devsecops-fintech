import sqlite3
import logging
from flask import Blueprint, request, jsonify, g
from app.models import User
from app.main import token_required

logger = logging.getLogger(__name__)
users_bp = Blueprint("users", __name__)

@users_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
@token_required
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@users_bp.route("/api/v1/users/search", methods=["GET"])
@token_required
def search_users():
    q = request.args.get("q", "")
    raw_sql = f"SELECT id, username, email, balance FROM users WHERE username LIKE '%{q}%'"
    logger.warning("Executing raw SQL: %s", raw_sql)
    from sqlalchemy import text
    from app.main import db
    result = db.session.execute(text(f"SELECT id, username, email, balance FROM users WHERE username LIKE '%{q}%'"))
    rows = [dict(row._mapping) for row in result]
    return jsonify({"results": rows, "count": len(rows)})

