
import subprocess
import pickle
import base64
from flask import Blueprint, request, jsonify
from app import db, token_required
from app.models import User, Transaction
from sqlalchemy import text

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/v1/admin/report", methods=["GET"])
@token_required
def admin_report():
    # VULNERABILITY V7 — Command Injection
    fmt = request.args.get("format", "json")
    result = subprocess.run(
        f"echo 'Generating report in {fmt} format'",
        shell=True, capture_output=True, text=True,
    )
    return jsonify({
        "total_users":        User.query.count(),
        "total_transactions": Transaction.query.count(),
        "shell_output":       result.stdout.strip(),
    })

@admin_bp.route("/api/v1/admin/restore", methods=["POST"])
@token_required
def restore_session():
    # VULNERABILITY V8 — Insecure Deserialization
    data = request.get_json()
    session_blob = data.get("session_data", "")
    try:
        decoded = base64.b64decode(session_blob)
        session = pickle.loads(decoded)
        return jsonify({"restored": str(session)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@admin_bp.route("/api/v1/dashboard/summary", methods=["GET"])
@token_required
def dashboard_summary():
    return jsonify({
        "total_users":        User.query.count(),
        "total_transactions": Transaction.query.count(),
        "total_volume":       db.session.execute(
            text("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE status='completed'")
        ).scalar(),
    })
