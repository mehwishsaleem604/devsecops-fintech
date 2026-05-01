
import time
from app import db

class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    balance       = db.Column(db.Float, default=10000.0)
    role          = db.Column(db.String(20), default="user")
    created_at    = db.Column(db.Float, default=time.time)

    def to_dict(self):
        return {
            "id":       self.id,
            "username": self.username,
            "email":    self.email,
            "balance":  self.balance,
            "role":     self.role,
        }

class Transaction(db.Model):
    __tablename__ = "transactions"
    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    card_number = db.Column(db.String(16))
    cvv         = db.Column(db.String(4))
    timestamp   = db.Column(db.Float, default=time.time)
    status      = db.Column(db.String(20), default="pending")

    def to_dict(self):
        return {
            "id":          self.id,
            "sender_id":   self.sender_id,
            "receiver_id": self.receiver_id,
            "amount":      self.amount,
            "status":      self.status,
            "timestamp":   self.timestamp,
            "card_number": self.card_number,  # PCI DSS violation
        }
