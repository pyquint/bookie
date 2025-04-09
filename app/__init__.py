from argon2 import PasswordHasher
from flask import Flask
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sassutils.wsgi import SassMiddleware

from config import Config

db = SQLAlchemy()
migrate = Migrate()
ph = PasswordHasher()
login_manager = LoginManager()
ckeditor = CKEditor()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)
    app.wsgi_app = SassMiddleware(
        app.wsgi_app, {"app": ("static/sass", "static/css", "/static/css")}
    )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    ckeditor.init_app(app)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app


from app import models
