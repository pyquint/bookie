import os
from urllib.parse import unquote

import bleach
import markdown
import sqlalchemy as sa
from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
)
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import and_, desc, inspect, or_

from app import db
from app.main import bp
from app.models import (
    CATALOGUES,
    SEARCHABLE_FIELDS,
    SEARCHABLE_RELATIONSHIP_FIELDS,
    SEARCHABLE_STRING_FIELDS,
    Author,
    Book,
    BookStatus,
    Comment,
    Genre,
    Publisher,
    User,
    getmodel,
)
from bookie import Character, UserFavorite


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
    """Get the value of a key from the `request.args` dictionary
    of the current request, or return the value of `default`."""
    value = request.args.get(key, default)
    return value if value else default


def process_book_query(
    request, book_query, title="Search Results", header="", *args, **kwargs
):
    sort_field = get_arg("sort", "bbe_score")
    sort_order = get_arg("order", "desc")
    sort_by_attr = getattr(Book, sort_field)
    order_by_query_clause = sort_by_attr if sort_order == "asc" else desc(sort_by_attr)

    sorted_query = book_query.order_by(order_by_query_clause)

    url_args = {k: v for k, v in request.args.items() if k and k != "page"}

    if "sort" in url_args:
        url_args["sort"] = sort_field
    if "order" in url_args:
        url_args["order"] = sort_order

    results, prev_page_url, next_page_url = paginate(
        request, sorted_query, *args, **url_args, **kwargs
    )

    endpoint_url = url_for(request.endpoint, *args, **url_args, **kwargs)

    search_parameters = {
        field: value
        for field, value in url_args.items()
        if field in SEARCHABLE_FIELDS and value != ""
    }

    return render_template(
        "search_results.html",
        endpoint_url=endpoint_url,
        title=title,
        header=header,
        args=url_args,
        results=results,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
        search_parameters=search_parameters,
        **kwargs,
    )


def build_like_query(args: dict[str, str], conjunction=and_):
    """Create a  LIKE query based on the provided arguments.

    The `conjunction` parameter can be either SQLAlchemy `and_` or `or_` function to combine the filters.
    """
    query = sa.select(Book)
    filters = []
    mapper = inspect(Book)

    for field in SEARCHABLE_STRING_FIELDS:
        if value := args.get(field):
            attr = getattr(Book, field)
            filters.append(attr.like(f"%{value}%"))

    for field, rel in SEARCHABLE_RELATIONSHIP_FIELDS.items():
        if value := args.get(field):
            related_model = getmodel(rel["related_model"])
            related_field = getattr(related_model, rel["related_field"])
            book_field = getattr(Book, field)

            relationship_property = mapper.relationships.get(field)

            if relationship_property.uselist:
                filters.append(book_field.any(related_field.like(f"%{value}%")))
            else:
                filters.append(book_field.has(related_field.like(f"%{value}%")))

    return query.filter(conjunction(*filters))


@bp.route("/search", methods=["GET"])
def search():
    query_all = request.args.get("all", "false") == "true"
    field = get_arg("field", "title")
    kwargs = dict()

    if field == "all":
        q = get_arg("query")
        args = {k: q for k in SEARCHABLE_FIELDS}
        query = build_like_query(args, or_)
        kwargs["header"] = f"Search results for all fields with '{q}':"
    else:
        args = request.args
        query = build_like_query(args, and_)
        kwargs["header"] = "Search results for:"

    if query_all:
        query = sa.select(Book)
        kwargs["header"] = "Book Catalogue"

    return process_book_query(request, query, **kwargs)


@bp.route("/advanced_search")
def advanced_search():
    return render_template("advanced_search.html")


@bp.route("/catalogues", methods=["GET"])
def catalogues():
    return render_template("catalogues.html", catalogues=SEARCHABLE_RELATIONSHIP_FIELDS)


@bp.route("/catalogue/<catalogue>", methods=["GET"])
def catalogue(catalogue):
    model = getmodel(CATALOGUES[catalogue]["related_model"])
    model_attr = CATALOGUES[catalogue]["related_field"]

    # `catalogue` may or may not have an s at the end, i.e. /catalogue/authors
    # but the url endpoint for an item of that catalogue should be singular, i.e. /author/<name>
    catalogue_endpoint = catalogue.rstrip("s")

    query = sa.select(model).order_by(model_attr)

    results, prev_page_url, next_page_url = paginate(
        request, query, per_page=100, catalogue=catalogue
    )

    return render_template(
        "catalogue.html",
        catalogue=catalogue,
        catalogue_endpoint=catalogue_endpoint,
        results=results,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
    )


def catalogue_books_view(model, name):
    name = unquote(name)
    query = sa.select(model).filter_by(name=name)
    model_object = db.first_or_404(query)
    header = f"{model.__name__}: {name}"
    return process_book_query(request, model_object.books, header=header, name=name)


@bp.route("/author/<path:name>", methods=["GET", "POST"])
def author(name):
    return catalogue_books_view(Author, name)


@bp.route("/genre/<path:name>", methods=["GET", "POST"])
def genre(name):
    return catalogue_books_view(Genre, name)


@bp.route("/publisher/<path:name>", methods=["GET", "POST"])
def publisher(name):
    return catalogue_books_view(Publisher, name)


@bp.route("/character/<path:name>", methods=["GET", "POST"])
def character(name):
    return catalogue_books_view(Character, name)


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
    comment = request.form.get("commentbox")
    comment = markdown.markdown(comment)

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
        args = {k: q for k in SEARCHABLE_FIELDS}
    else:
        args = request.args.to_dict()

    query = build_like_query(args, or_)
    results = db.session.scalars(query)

    # TODO turn relationship fields into serializable (to_dict() perhaps?)
    response = {"result": [book.to_dict() for book in results]}

    return jsonify(response)


@bp.route("/api/comments/<int:id>", methods=["GET"])
def get_comment(id):
    return db.get_or_404(Comment, id).to_dict()
