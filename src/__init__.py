import sentry_sdk
from os import path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from sentry_sdk.integrations.flask import FlaskIntegration

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    templates_path = path.abspath(path.join(path.dirname(__file__), "..", "templates"))
    static_path = path.abspath(
        path.join(path.dirname(__file__), "..", "static")
    )

    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    app.config.from_object(Config)

    sentry_sdk.init(dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()])

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = "main.login"
    bcrypt.init_app(app)

    from src.views import bp

    app.register_blueprint(bp)

    return app
