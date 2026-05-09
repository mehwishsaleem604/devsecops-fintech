import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key-123")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///fintech.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secure-random-string-here")
JWT_ALGO = "HS256"
JWT_EXP_SECS = int(os.getenv("JWT_EXP_SECS", 86400))

