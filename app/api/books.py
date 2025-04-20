import sqlalchemy as sa
from flask import request

from app import db
from app.api import api
from app.models import Book


@api.route("/books", methods=["GET"])
def get_books():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    return Book.to_collection_dict(sa.select(Book), page, per_page, "api.get_users")


@api.route("/books/<id>", methods=["GET"])
def get_book(id):
    return db.get_or_404(Book, id).to_dict()
