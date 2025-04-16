import json
import os

import markdown
import sqlalchemy as sa
from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy import desc

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
    query_all = request.args.get("all", "false") == "true"

    if not query_all:
        for column in Book.__table__.columns:
            if value := request.args.get(column.name):
                attr = getattr(Book, column.name)
                query = query.filter(attr.like(f"%{value}%"))

    sort_field = request.args.get("sort", "num_ratings")
    sort_order = request.args.get("order", "desc")
    sort_by_attr = getattr(Book, sort_field)
    order_by_query_clause = sort_by_attr if sort_order == "asc" else desc(sort_by_attr)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    sorted_query = query.order_by(order_by_query_clause)
    results = db.paginate(sorted_query, page=page, per_page=per_page, error_out=False)

    search_parameters = {
        param: val for param, val in request.args.items() if param != "page"
    }

    prev_page_url = (
        url_for("main.search", **search_parameters, page=results.page - 1)
        if results.has_prev
        else None
    )

    next_page_url = (
        url_for("main.search", **search_parameters, page=results.page + 1)
        if results.has_next
        else None
    )

    return render_template(
        "search_results.html",
        args=search_parameters,
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

    # query = sa.select(Comment).filter(Comment.book_id == book_id)
    # comments = db.session.scalars(query)
    # book_status = db.session.get(BookStatus, (current_user.id, book_id))

    return render_template(
        "book.html",
        book=book,
        from_results_page=(
            request.referrer
            if request.referrer != request.url
            else url_for("main.index")
        ),
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
    favorite = db.session.get(UserFavorite, (user_id, book_id))

    user = db.session.get(User, user_id)
    print(user.favorite_books)

    if favorite:
        db.session.delete(favorite)
        response = jsonify(favorited=0, message="Successfully removed from favorites.")
    else:
        new_favorite = UserFavorite(**data)
        db.session.add(new_favorite)
        response = jsonify(favorited=1, message="Successfully added to favorites!")

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
