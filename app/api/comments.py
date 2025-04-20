import sqlalchemy as sa
from flask import request

from app import db
from app.api import api
from app.models import Comment


@api.route("/comments", methods=["GET"])
def get_comments():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    return Comment.to_collection_dict(
        sa.select(Comment), page, per_page, "api.get_users"
    )


@api.route("/comments/<int:id>", methods=["GET"])
def get_comment(id):
    return db.get_or_404(Comment, id).to_dict()


@api.route("/comments", methods=["POST"])
def post_comment(book_id):
    data = request.get_json()
    if "book_data" not in data or "body" not in data:
        # return bad_request({"error": "Invalid data"}, 400)
        pass
    return db.get_or_404(Comment, id).to_dict()
