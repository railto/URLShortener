import sentry_sdk
from datetime import datetime
import string
import random

from flask import Flask, render_template, redirect, flash, url_for, request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from sentry_sdk.integrations.flask import FlaskIntegration

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

sentry_sdk.init(dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()])

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
bcrypt = Bcrypt(app)
login.login_view = "login"


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
            password, app.config["BCRYPT_LOG_ROUNDS"]
        ).decode()


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    link = db.Column(db.String(16), unique=True)
    visits = db.Column(db.Integer)
    url = db.Column(db.String(255), unique=True)


class LoginForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Email Address"},
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Sign In")


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/")
@login_required
def index():
    links = Link.query.all()
    return render_template("index.html", links=links)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            flash("Invalid email address or password")
            return render_template("login.html", title="Sign In", form=form), 401
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        flash("You have been logged in")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out")
    return redirect(url_for("index"))


@app.route("/link", methods=["post"])
@login_required
def add_link():
    form = request.form
    link = create_link(form)
    return link


@app.route("/link/<int:id>", methods=["delete"])
@login_required
def delete_link(id):
    link = Link.query.filter_by(id=id).first()
    db.session.delete(link)
    db.session.commit()
    return jsonify(success=True)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def route(path):
    url = Link.query.filter_by(link=path).first_or_404()
    url.visits = Link.visits + 1
    db.session.commit()
    if "http://" not in url.url and "https://" not in url.url:
        link = "http://" + url.url
    else:
        link = url.url
    return redirect(link, code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


def create_link(params):
    try:
        url = params["url"]
        if "link" in params and len(params["link"]) > 0:
            link = params["link"]
        else:
            link = link_generator()
        item = Link(link=link, visits="0", url=url, user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        return jsonify(success=True, link=link)
    except IntegrityError:
        return jsonify(success=False)


def link_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


if __name__ == "__main__":
    app.run()
