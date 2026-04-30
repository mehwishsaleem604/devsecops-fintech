import logging
from flask_talisman import Talisman 
from werkzeug.security import generate_password_hash
from app import create_app, db 
from app.models import User, Transaction

logger = logging.getLogger(__name__)

app = create_app()

Talisman(app, force_https=False)

def seed_db():
    with app.app_context(): 
        if User.query.count() == 0:
            users = [
                User(username="alice",   password_hash=generate_password_hash("alice123"),
                     email="alice@fintech.io",   balance=50000.0, role="admin"),
                User(username="bob",     password_hash=generate_password_hash("bob123"),
                     email="bob@fintech.io",     balance=25000.0),
                User(username="charlie", password_hash=generate_password_hash("charlie123"),
                     email="charlie@fintech.io", balance=15000.0),
            ]
            
            db.session.bulk_save_objects(users)
            db.session.commit()
            logger.info("Database seeded")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_db()
    app.run(host="0.0.0.0", port=5000, debug=True)