from argon2 import PasswordHasher
from flask import Flask
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sassutils.wsgi import SassMiddleware

db = SQLAlchemy()
ph = PasswordHasher()


def create_app():
    app = Flask(__name__, template_folder="templates")

    app.wsgi_app = SassMiddleware(
        app.wsgi_app, {"app": ("static/sass", "static/css", "/static/css")}
    )

    app.config["SECRET_KEY"] = "eab1049363d660aa39c1fb8bf5197ba2"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookie.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from models import User
    from routes import register_routes

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)

    register_routes(app, db, ph)

    migrate = Migrate(app, db)

    ckeditor = CKEditor()
    ckeditor.init_app(app)

    with app.app_context():
        if db.engine.url.drivername == "sqlite":
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)

    return app
