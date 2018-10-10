from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, http_auth_required
from dotenv import load_dotenv
import os
import string
import random

# Check to see if we have a .env file and load it if we do
if os.path.exists(os.path.join(os.path.dirname(__file__), '.env')):
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Start building the app
app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('DEBUG')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Setup DB
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(16), unique=True)
    visits = db.Column(db.Integer)
    url = db.Column(db.String(255), unique=True)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/', methods=['get'])
@login_required
def home(page=1):
    links = Link.query.all()
    return render_template('index.html', links=links, loggedin=True)


@app.route('/link', methods=['post'])
@login_required
def add_link():
    form = request.form
    link = create_link(form)
    return link


@app.route('/api/link', methods=['post'])
@http_auth_required
def api_add_link():
    input = request.get_json()
    link = create_link(input)
    return link


@app.route('/link/<int:id>', methods=['delete'])
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
        link = "http://"+url.url
    else:
        link = url.url
    return redirect(link, code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def create_link(params):
    try:
        url = params['url']
        if 'link' in params and len(params['link']) > 0:
            link = params['link']
        else:
            link = link_generator()
        item = Link(link=link, visits='0', url=url, user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        return jsonify(success=True, link=link)
    except IntegrityError:
        return jsonify(success=False)


def link_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


if __name__ == '__main__':
    app.run()
