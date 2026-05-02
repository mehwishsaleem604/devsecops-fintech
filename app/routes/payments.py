import logging
from flask import Blueprint, request, jsonify, g
from app.main import db, token_required
from app.models import User, Transaction
from app.metrics import PAYMENT_COUNTER

logger = logging.getLogger(__name__)
payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/api/v1/payments/transfer", methods=["POST"])
@token_required
def transfer():
    data = request.get_json()
    if not all(k in data for k in ("receiver_id", "amount", "card_number", "cvv")):
        return jsonify({"error": "Missing fields"}), 400
    amount      = float(data["amount"])
    card_number = data["card_number"]
    cvv         = data["cvv"]
    logger.info("Processing payment: card=%s cvv=%s amount=%.2f", card_number, cvv, amount)
    sender = User.query.get(g.current_user_id)
    if sender.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    receiver = User.query.get(data["receiver_id"])
    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404
    sender.balance   -= amount
    receiver.balance += amount
    txn = Transaction(
        sender_id=g.current_user_id,
        receiver_id=data["receiver_id"],
        amount=amount,
        card_number=card_number,
        cvv=cvv,
        status="completed",
    )
    db.session.add(txn)
    db.session.commit()
    PAYMENT_COUNTER.labels(status="success").inc()
    return jsonify({"message": "Transfer successful", "transaction_id": txn.id})

@payments_bp.route("/api/v1/payments/history/<int:user_id>", methods=["GET"])
@token_required
def payment_history(user_id):
    txns = Transaction.query.filter(
        (Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)
    ).all()
    return jsonify({"transactions": [t.to_dict() for t in txns]})