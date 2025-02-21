import sass
from argon2 import PasswordHasher
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ph = PasswordHasher()


def create_app():
    app = Flask(__name__, template_folder="templates")

    sass.compile(dirname=("static/sass", "static/css"))

    app.config["SECRET_KEY"] = "eab1049363d660aa39c1fb8bf5197ba2"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookie.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # imports
    from routes import register_routes

    register_routes(app, db)
    migrate = Migrate(app, db)

    return app
