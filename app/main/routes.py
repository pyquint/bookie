import json
import os
import time

import markdown
import sqlalchemy as sa
from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy import desc, exc

from app import db
from app.main import bp
from app.models import Book, BookStatus, Comment, User
from bookie import UserFavorite


@bp.route("/")
@bp.route("/index")
@bp.route("/home")
def index():
    return render_template("index.html")


@bp.route("/search", methods=["GET"])
def search():
    query = sa.select(Book)
    all = request.args.get("all", "false")

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
    book = db.session.get(Book, book_id)

    if book is None:
        return redirect("/")

    query = sa.select(Comment).filter(Comment.book_id == book_id)
    comments = db.session.scalars(query)

    if current_user.is_authenticated:
        book_status = current_user.get_book_status(book_id)
    else:
        book_status = None

    print("\n", book_status, "\n")

    return render_template(
        "book.html",
        book=book,
        from_results_page=(
            request.referrer
            if request.referrer != request.url
            else url_for("main.index")
        ),
        comments=comments,
        book_status=book_status,
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


@bp.route("/book/<book_id>/delete_comment?<comment_id>")
def delete_comment(book_id, comment_id):
    comment = db.session.get(Comment, comment_id)
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for("main.book", book_id=book_id))


@bp.route("/user/<username>")
def user(username):
    query = sa.select(User).where(User.username == username)
    user = db.session.scalar(query)

    return render_template("user.html", user=user)


@bp.route("/settings")
@login_required
def settings():
    return render_template("auth/settings.html")


@bp.route("/update_pp", methods=["GET", "POST"])
@login_required
def update_pp():
    if request.method == "POST":
        if "file" not in request.files:
            print("pp not in request... ", request.files)
            return redirect(request.referrer)

        file = request.files["file"]

        if file.filename == "":
            print("filename is empty... ", request.files)
            return redirect(request.referrer)

        if file:
            # os.path.join's backslash delimiter turns into
            # %5C (special HTML character code for backslash)
            # when treated as a path, e.g url_for('static', filename=filename)

            # forward slashes do not have this issue on my machinem here using f-strings
            # but I worry it might pose incompatibility with other file systems

            # file_path = f"{current_app.config["UPLOAD_FOLDER"]}/pp/{file.filename}"

            # replacing \ with / works, but I have no idea on different file systems
            # probably still has the same incompatibility issues

            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], "pp", file.filename
            ).replace("\\", "/")
            save_path = os.path.join(current_app.static_folder, file_path)

            current_user.change_pp(file_path)
            file.save(save_path)
            db.session.commit()

        return redirect(url_for("main.user", username=current_user.username))


@bp.post("/update_status")
@login_required
def update_status():
    status_id = request.form.get("status_id", type=int)

    book_id = request.form.get("book_id")
    book = db.session.get(Book, book_id)

    finished_chapters = request.form.get("finished_chapters", type=int)

    query = sa.select(BookStatus).filter_by(book=book, user=current_user)
    book_status = db.session.scalar(query)

    if book_status:
        book_status.finished_chapters = (
            finished_chapters or book_status.finished_chapters
        )
        book_status.reading_status_id = status_id
    else:
        book_status = BookStatus(
            user=current_user,
            reading_status_id=status_id,
            book=book,
            finished_chapters=finished_chapters,
        )
        db.session.add(book_status)

    db.session.commit()
    print("\nsuccessful:", book_status, "\n")

    return jsonify(message="Status successfully updated.")


@bp.post("/toggle_favorite")
@login_required
def toggle_favorite():
    data = request.get_json()
    user_id = int(data["user_id"])
    book_id = data["book_id"]

    # favorite = UserFavorite(**data)
    # fav = UserFavorite.query.get((user_id, book_id))
    favorite = db.session.get(UserFavorite, (user_id, book_id))
    print("query:", favorite)
    # print("exists:", sa.select(UserFavorite.user_id).where(user_id).exists())

    user = db.session.get(User, user_id)
    print(user.favorite_books)
    print("\nalready in favorites", favorite in user.favorite_books, "\n")

    if favorite:
        db.session.delete(favorite)
        response = jsonify(favorited=0, message="Successfully removed from favorites.")
    else:
        new_favorite = UserFavorite(**data)
        db.session.add(new_favorite)
        response = jsonify(favorited=1, message="Successfully added to favorites!")
        print("\nnew favorite: ", new_favorite, "\n")

    db.session.commit()
    return response


@bp.route("/api/search")
def api_search():
    type = request.args.get("type", "title")
    query_string = request.args.get("query", "")
    query = sa.select(Book).filter(getattr(Book, type).like(f"%{query_string}%"))
    results = db.session.scalars(query)

    response = {
        "result": [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "publisher": book.publisher,
                "ISBN": book.isbn,
            }
            for book in results
        ]
    }

    return jsonify(response)


@bp.route("/api/get_comment")
def get_comment():
    comment_id = request.args.get("comment_id")

    query = sa.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(query)

    comment_dict = comment.__dict__
    comment_dict.pop("_sa_instance_state")

    return json.dumps(comment_dict, default=str)
