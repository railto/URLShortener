import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    FLASK_ENV = os.environ.get("FLASK_ENV") or "production"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 12
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
