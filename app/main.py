import time
import logging
from functools import wraps
import jwt
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
import app.config as config

db = SQLAlchemy()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGO])
            g.current_user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def create_app(testing=False):
    app = Flask(__name__)
    app.config["SECRET_KEY"]                     = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"]        = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)

    if not testing:
        with app.app_context():
            db.create_all()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("fintech_app.log")],
    )

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def record_metrics(response):
        latency = time.time() - g.start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or "unknown",
            status=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(endpoint=request.endpoint or "unknown").observe(latency)
        return response

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "service": "fintech-api", "version": "1.0.0"})

    @app.route("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    from app.routes.auth     import auth_bp
    from app.routes.users    import users_bp
    from app.routes.payments import payments_bp
    from app.routes.admin    import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)

    return app

app = create_app()


