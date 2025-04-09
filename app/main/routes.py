import json

import markdown
import sqlalchemy as sa
from flask import redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy import desc

from app import db
from app.main import bp
from app.models import Book, Comment, User


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@bp.route("/search", methods=["GET"])
def search():
    query = sa.select(Book)
    all = request.args.get("all", "true")

    if all == "false":
        for column in Book.__table__.columns:
            if arg_value := request.args.get(column.name):
                print(arg_value)
                query = query.filter(getattr(Book, column.name).like(f"%{arg_value}%"))

    sort = request.args.get("sort", "num_ratings")
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", "desc")
    per_page = request.args.get("per_page", 10, type=int)

    sortby_attr = getattr(Book, sort)

    if order == "desc":
        sorted_query = query.order_by(desc(sortby_attr))
    else:
        sorted_query = query.order_by(sortby_attr)

    results = db.paginate(sorted_query, page=page, per_page=per_page, error_out=False)

    params = request.args.to_dict()
    params.pop("page")

    prev_page_url = (
        url_for("main.search", **params, page=results.page - 1)
        if results.has_prev
        else None
    )

    next_page_url = (
        url_for("main.search", **params, page=results.page + 1)
        if results.has_next
        else None
    )

    return render_template(
        "search_results.html",
        args=request.args,
        sort=sort,
        results=results,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
    )


@bp.route("/advanced_search")
def advanced_search():
    return render_template("advanced_search.html")


@bp.route("/book/<book_id>", methods=["GET"])
def book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return redirect("/")
    comments = Comment.query.filter(Comment.book_id == book_id)
    return render_template(
        "book.html",
        book=book,
        from_results_page=(
            request.referrer
            if request.referrer != request.url
            else url_for("main.index")
        ),
        comments=comments,
    )


@bp.post("/book/<book_id>")
def post_comment(book_id):
    print(request.form.get("ckeditor"))
    comment = markdown.markdown(request.form.get("commentbox"))

    if comment:
        # date_created = datetime.now().isoformat()

        comment = Comment(
            book_id=book_id,
            user_id=current_user.id,
            comment=comment,
            # date_created=date_created,
        )

        db.session.add(comment)
        db.session.commit()

    # prevents resubmitting of comment when reloadign the page immedately after posting
    return redirect(url_for("main.book", book_id=book_id))


@bp.route("/get_comment")
def get_comment():
    comment_id = request.args.get("comment_id", "")
    comment = Comment.query.filter_by(id=comment_id).first()
    comment_dict = comment.__dict__
    comment_dict.pop("_sa_instance_state")
    return json.dumps(comment_dict, default=str)


@bp.route("/book/<book_id>/delete_comment?<comment_id>")
def delete_comment(book_id, comment_id):
    Comment.query.filter_by(id=comment_id).delete()
    db.session.commit()
    return redirect(url_for("main.book", book_id=book_id))


@bp.route("/user/<username>")
def user(username):
    user = User.query.filter(User.username == username).first()
    return render_template("user.html", user=user)


@bp.route("/settings")
@login_required
def settings():
    return render_template("auth/settings.html")
