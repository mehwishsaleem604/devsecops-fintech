"""
Test suite for the DevSecOps Fintech API.
These tests run in the GitHub Actions pipeline (Stage 2: Build + Test).
"""

import json
import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, db, seed_db 

# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        seed_db()
        yield app.test_client()
        db.drop_all()

def _login(client, username="alice", password="alice123"):
    rv = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return rv.get_json()["token"]


# ─────────────────────────────────────────────
# Health & Metrics (Developer 4 focus)
# ─────────────────────────────────────────────
class TestInfraEndpoints:
    def test_health_returns_200(self, client):
        rv = client.get("/health")
        assert rv.status_code == 200
        assert rv.get_json()["status"] == "healthy"

    def test_metrics_endpoint_returns_prometheus_format(self, client):
        rv = client.get("/metrics")
        assert rv.status_code == 200
        # Check for standard prometheus metric
        assert b"flask_http_request_total" in rv.data or b"http_requests_total" in rv.data


# ─────────────────────────────────────────────
# Security & PCI DSS (Developer 2 & 3 focus)
# ─────────────────────────────────────────────
class TestSecurityCompliance:
    def test_security_headers_present(self, client):
        """REQ-6.5: Verify security headers are set (XSS protection, etc.)"""
        rv = client.get("/health")
        # Flask-Talisman ye headers add karta hy
        assert "X-Frame-Options" in rv.headers
        assert "X-Content-Type-Options" in rv.headers

    def test_no_cvv_in_response(self, client):
        """REQ-3.3: Verify sensitive CVV is never returned in API response"""
        token = _login(client)
        rv = client.post("/api/v1/payments/transfer",
                         headers={"Authorization": f"Bearer {token}"},
                         json={
                             "receiver_id": 2,
                             "amount": 100.0,
                             "card_number": "4111111111111111",
                             "cvv": "123",
                         })
        assert "cvv" not in str(rv.data).lower()


# ─────────────────────────────────────────────
# Auth & Payments (Existing Logic)
# ─────────────────────────────────────────────
class TestAuth:
    def test_register_new_user(self, client):
        rv = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "password": "testpass123",
            "email":     "test@fintech.io",
        })
        assert rv.status_code == 201

    def test_login_invalid_password_returns_401(self, client):
        rv = client.post("/api/v1/auth/login", json={
            "username": "alice",
            "password": "wrongpassword",
        })
        assert rv.status_code == 401

class TestPayments:
    def test_transfer_insufficient_funds(self, client):
        token = _login(client, username="charlie", password="charlie123")
        rv = client.post("/api/v1/payments/transfer",
                         headers={"Authorization": f"Bearer {token}"},
                         json={
                             "receiver_id": 1,
                             "amount": 9999999.0,
                             "card_number": "4111111111111111",
                             "cvv": "123",
                         })
        assert rv.status_code == 400