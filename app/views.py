from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from app import bcrypt, db
from app.forms import LoginForm
from app.utils import create_link
from app.models import User, Link

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def index():
    links = Link.query.all()
    return render_template("index.html", links=links)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            return render_template("login.html", title="Sign In", form=form), 401
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("main.index"))


@bp.route("/link", methods=["post"])
@login_required
def add_link():
    form = request.form
    link = create_link(form)
    return link


@bp.route("/link/<int:id>", methods=["delete"])
@login_required
def delete_link(id):
    link = Link.query.filter_by(id=id).first()
    db.session.delete(link)
    db.session.commit()
    return jsonify(success=True)


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def route(path):
    url = Link.query.filter_by(link=path).first_or_404()
    url.visits = Link.visits + 1
    db.session.commit()
    if "http://" not in url.url and "https://" not in url.url:
        link = "http://" + url.url
    else:
        link = url.url
    return redirect(link, code=302)


@bp.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
