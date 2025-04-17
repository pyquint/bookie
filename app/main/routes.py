import json
import os

import markdown
import sqlalchemy as sa
from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
)
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import desc

from app import SEARCHABLE_RELATIONSHIP_FIELDS, SEARCHABLE_STRING_FIELDS, db
from app.main import bp
from app.models import Author, Book, BookStatus, Comment, Genre, Publisher, User
from bookie import UserFavorite


@bp.route("/")
@bp.route("/index")
@bp.route("/home")
def index():
    return render_template("index.html")


def paginate(
    request, book_query, per_page=10, error_out=False, *args, **kwargs
) -> tuple[Pagination, str, str]:
    """Paginate the query results and return the pagination object along with previous and next page URLs."""

    page = request.args.get("page", 1, type=int)
    pagination = db.paginate(
        book_query, page=page, per_page=per_page, error_out=error_out
    )

    previous_page_url = (
        url_for(request.endpoint, page=pagination.page - 1, *args, **kwargs)
        if pagination.has_prev
        else None
    )

    next_page_url = (
        url_for(request.endpoint, page=pagination.page + 1, *args, **kwargs)
        if pagination.has_next
        else None
    )
    return pagination, previous_page_url, next_page_url


def get_arg(key: str, default=None):
    """Get the value of a key from the request.args dictionary, or return the default value."""
    value = request.args.get(key, default)
    return value if value else default


def process_book_query(
    request, book_query, title="Search Results", header="", **kwargs
):
    sort_field = get_arg("sort", "num_ratings")
    sort_order = get_arg("order", "desc")
    sort_by_attr = getattr(Book, sort_field)
    order_by_query_clause = sort_by_attr if sort_order == "asc" else desc(sort_by_attr)

    sorted_query = book_query.order_by(order_by_query_clause)

    search_parameters = {k: v for k, v in request.args.items() if k and k != "page"}

    if "sort" in search_parameters:
        search_parameters["sort"] = sort_field
    if "order" in search_parameters:
        search_parameters["order"] = sort_order

    results, prev_page_url, next_page_url = paginate(
        request, sorted_query, **search_parameters, **kwargs
    )

    endpoint_url = url_for(request.endpoint, **kwargs)

    search_args = [
        f"{field}='{value}'"
        for field, value in search_parameters.items()
        if field in SEARCHABLE_STRING_FIELDS + SEARCHABLE_RELATIONSHIP_FIELDS and value
    ]

    return render_template(
        "search_results.html",
        endpoint_url=endpoint_url,
        title=title,
        header=header,
        args=search_parameters,
        results=results,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
        search_args=search_args,
        **kwargs,
    )


def and_like_query(args: dict, default=""):
    """Create a type-agnostic LIKE query based on the provided arguments."""
    query = sa.select(Book)

    for field in SEARCHABLE_STRING_FIELDS:
        if value := args.get(field):
            query = query.filter(getattr(Book, field).like(f"%{value}%"))

    for field in SEARCHABLE_RELATIONSHIP_FIELDS:
        if value := args.get(field):
            match field:
                case "authors":
                    filter = Book.authors.any(Author.name.like(f"%{value}%"))
                case "genres":
                    filter = Book.genres.any(Genre.name.like(f"%{value}%"))
                case "publisher":
                    filter = Book.publisher.has(Publisher.name.like(f"%{value}%"))

            query = query.filter(filter)

    return query


def or_like_query(args: dict):
    """Create a type-agnostic LIKE query based on the provided arguments."""
    query = sa.select(Book)
    or_conditions = set()

    for field in SEARCHABLE_STRING_FIELDS:
        if value := args.get(field):
            attr = getattr(Book, field)
            or_conditions.add(attr.like(f"%{value}%"))

    for field in SEARCHABLE_RELATIONSHIP_FIELDS:
        if value := args.get(field):
            match field:
                case "authors":
                    cond = Book.authors.any(Author.name.like(f"%{value}%"))
                case "genres":
                    cond = Book.genres.any(Genre.name.like(f"%{value}%"))
                case "publisher":
                    cond = Book.publisher.has(Publisher.name.like(f"%{value}%"))

            or_conditions.add(cond)

    # query = query.filter(Book.authors.any(Author.name.like(f"%{"row"}%")))

    if or_conditions:
        query = query.filter(sa.or_(*or_conditions))

    return query


@bp.route("/search", methods=["GET"])
def search():
    query_all = request.args.get("all", "false") == "true"
    field = get_arg("field", "title")
    kwargs = dict()

    if field == "all":
        q = get_arg("query")
        args = {k: q for k in SEARCHABLE_STRING_FIELDS + SEARCHABLE_RELATIONSHIP_FIELDS}
        query = or_like_query(args)
        kwargs["header"] = f"Search results for all fields with '{q}'"
    else:
        args = request.args
        query = and_like_query(args)
        kwargs["header"] = "Search results for:"

    kwargs["header"] = "Book Catalogue" if query_all else kwargs["header"]

    query = sa.select(Book) if query_all else query

    return process_book_query(request, query, **kwargs)


@bp.route("/advanced_search")
def advanced_search():
    return render_template("advanced_search.html")


@bp.route("/catalogues", methods=["GET"])
def catalogues():
    return render_template("catalogues.html", catalogues=SEARCHABLE_RELATIONSHIP_FIELDS)


@bp.route("/catalogue/<catalogue>", methods=["GET"])
def catalogue(catalogue):
    match catalogue:
        case "authors" | "author":
            model = Author
            catalogue = "author"
        case "genres" | "genre":
            model = Genre
            catalogue = "genre"
        case "publisher":
            model = Publisher

    query = sa.select(model).order_by(model.name)
    results, prev_page_url, next_page_url = paginate(
        request, query, per_page=100, catalogue=catalogue
    )

    return render_template(
        "catalogue.html",
        catalogue=catalogue,
        results=results,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
    )


@bp.route("/author/<name>", methods=["GET", "POST"])
def author(name):
    query = sa.select(Author).filter_by(name=name)
    author = db.first_or_404(query)

    return process_book_query(
        request,
        author.books,
        name,
        f"Author: {author.name}",
        name=name,
    )


@bp.route("/genre/<name>", methods=["GET", "POST"])
def genre(name):
    query = sa.select(Genre).filter_by(name=name)
    genre = db.first_or_404(query)

    return process_book_query(
        request,
        genre.books,
        name,
        f"Genre: {genre.name}",
        name=name,
    )


@bp.route("/publisher/<name>", methods=["GET", "POST"])
def publisher(name):
    query = sa.select(Publisher).filter_by(name=name)
    genre = db.first_or_404(query)

    return process_book_query(
        request,
        genre.books,
        name,
        f"Publisher: {genre.name}",
        name=name,
    )


@bp.route("/book/<book_id>", methods=["GET"])
def book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return redirect("/")

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


@bp.route("/update_pp", methods=["GET", "POST"])
@login_required
def update_pp():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.referrer)

        file = request.files["file"]

        if file.filename == "":
            return redirect(request.referrer)

        if file:
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

    return jsonify(message="Status successfully updated.")


@bp.post("/toggle_favorite")
@login_required
def toggle_favorite():
    data = request.get_json()
    user_id = int(data["user_id"])
    book_id = data["book_id"]
    favorite = db.session.get(UserFavorite, (user_id, book_id))

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
    field = get_arg("field", "title")
    if field == "all":
        q = get_arg("query")
        args = {k: q for k in SEARCHABLE_STRING_FIELDS + SEARCHABLE_RELATIONSHIP_FIELDS}
    else:
        args = request.args.to_dict()

    query = or_like_query(args)
    results = db.session.scalars(query)

    # TODO turn relationship fields into serializable (to_dict() perhaps?)
    response = {
        "result": [
            {
                "id": book.id,
                "title": book.title,
                "description": book.description,
                "ISBN": book.isbn,
                # "authors": book.authors,
                # "publisher": book.publisher,
                # "genres": book.genres,
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
