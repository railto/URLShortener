from datetime import datetime

from flask import current_app
from flask_login import UserMixin

from src import db, bcrypt, login


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), index=True, unique=True)
    password = db.Column(db.String(255))
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config["BCRYPT_LOG_ROUNDS"]
        ).decode()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    link = db.Column(db.String(16), unique=True, index=True)
    notes = db.Column(db.Text(), nullable=True)
    visits = db.Column(db.Integer)
    url = db.Column(db.String(255))
