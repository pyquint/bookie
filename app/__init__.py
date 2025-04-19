from argon2 import PasswordHasher
from flask import Flask
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sassutils.wsgi import SassMiddleware
from sqlalchemy import MetaData

from config import Config

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate(render_as_batch=True)
ph = PasswordHasher()
login_manager = LoginManager()
ckeditor = CKEditor()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)
    app.wsgi_app = SassMiddleware(
        app.wsgi_app,
        {
            "app": {
                "sass_path": "static/sass",
                "css_path": "static/css",
                "wsgi_path": "/static/css",
                "strip_extension": False,
            }
        },
    )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    ckeditor.init_app(app)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.models import (
        CATALOGUES,
        SEARCHABLE_FIELDS,
        SEARCHABLE_RELATIONSHIP_FIELDS,
        SEARCHABLE_STRING_FIELDS,
        SORTABLE_FIELDS,
    )

    @app.context_processor
    def inject_searchables():
        return dict(
            SEARCHABLE_STRING_FIELDS=SEARCHABLE_STRING_FIELDS,
            SEARCHABLE_LIST_FIELDS=SEARCHABLE_RELATIONSHIP_FIELDS,
            SEARCHABLE_FIELDS=SEARCHABLE_FIELDS,
            CATALOGUES=CATALOGUES,
            SORTABLE_FIELDS=SORTABLE_FIELDS,
        )

    @app.template_filter("rstrip")
    def rstrip_filter(s, suffix):
        return s.rstrip(suffix)

    return app


from app import models
