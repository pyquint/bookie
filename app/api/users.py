import sqlalchemy as sa
from flask import request

from app import db
from app.api import api
from app.models import User


@api.route("/users", methods=["GET"])
def get_users():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    return User.to_collection_dict(sa.select(User), page, per_page, "api.get_users")


@api.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    return db.get_or_404(User, id).to_dict()
