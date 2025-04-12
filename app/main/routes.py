import json
import os

import markdown
import sqlalchemy as sa
from flask import current_app, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy import desc

from app import db
from app.main import bp
from app.models import Book, BookStatus, Comment, User
from bookie import ReadingStatus


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
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

    print("\ncurrent user status:", book_status, "\n")

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


@bp.route("/get_comment")
def get_comment():
    comment_id = request.args.get("comment_id", "")

    query = sa.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalars(query).first()

    comment_dict = comment.__dict__
    comment_dict.pop("_sa_instance_state")

    return json.dumps(comment_dict, default=str)


@bp.route("/book/<book_id>/delete_comment?<comment_id>")
def delete_comment(book_id, comment_id):
    comment = db.session.get(Comment, comment_id)
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for("main.book", book_id=book_id))


@bp.route("/user/<username>")
def user(username):
    query = sa.select(User).where(User.username == username)
    user = db.session.scalars(query).first()

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
    print("\n", request.form, "\n")

    status_id = request.form.get("status_id", type=int)
    # reading_status = db.session.get(ReadingStatus, status_id)

    book_id = request.form.get("book_id")
    book = db.session.get(Book, book_id)

    finished_chapters = request.form.get("finished_chapters", type=int)

    query = sa.select(BookStatus).filter_by(book=book, user=current_user)
    book_status = db.session.scalars(query).first()

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

    return redirect(request.referrer)
