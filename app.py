from flask import Flask, render_template, url_for, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user
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
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')
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
def home():
    links = Link.query.all()
    return render_template('index.html', links=links, loggedin=True)

@app.route('/link', methods=['post'])
@login_required
def add_link():
    form = request.form
    url = form['url']
    link = link_generator()
    item = Link(link = link, visits='0', url=url, user_id=current_user.id)
    db.session.add(item)
    db.session.commit()
    print(item)
    return jsonify(success=True)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def route(path):
    url = Link.query.filter_by(link=path).first_or_404()
    url.visits = Link.visits + 1
    db.session.commit()
    return redirect(url.url, code=302)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def link_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    app.run()
