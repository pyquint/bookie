import sass
from flask import Flask, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from forms import LoginForm, SignupForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

sass.compile(dirname=("static/sass", "static/css"))

app.config["SECRET_KEY"] = "eab1049363d660aa39c1fb8bf5197ba2"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookie.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


class Book(db.Model):
    __tablename__ = "book_fts"

    book_id = db.Column(db.String, primary_key=True)
    isbn = db.Column(db.String)
    title = db.Column(db.String)
    series = db.Column(db.String, nullable=True)
    author = db.Column(db.String, nullable=True)
    rating = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    language = db.Column(db.String, nullable=True)
    genres = db.Column(db.String, nullable=True)
    characters = db.Column(db.String, nullable=True)
    book_format = db.Column(db.String, nullable=True)
    edition = db.Column(db.String, nullable=True)
    pages = db.Column(db.String, nullable=True)
    publisher = db.Column(db.String, nullable=True)
    publish_date = db.Column(db.String, nullable=True)
    awards = db.Column(db.String, nullable=True)
    num_ratings = db.Column(db.String, nullable=True)
    ratings_by_stars = db.Column(db.String, nullable=True)
    liked_percent = db.Column(db.String, nullable=True)
    setting = db.Column(db.String, nullable=True)
    cover_img = db.Column(db.String, nullable=True)
    bbe_score = db.Column(db.String, nullable=True)
    bbe_votes = db.Column(db.String, nullable=True)
    price = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"


@app.route("/", methods=["POST", "GET"])
def index():
    books = Book.query.limit(10).all()
    return render_template("index.html", books=books)


@app.route("/signup")
def signup():
    form = SignupForm()
    return render_template("signup.html", form=form)


@app.route("/login")
def login():
    form = SignupForm()
    return render_template("login.html", form=form)


@app.route("/search", methods=["GET"])
def search():
    """
    This query returns duplicate results, even if the search type is ISBN
    which is supposedly unique. Do note that some of the entries do have
    the same ISBN consisting of all 9s.

    The idea was to get the exact matches first then similar matches.

        dbquery = '''
            SELECT *, 1 AS exact_match_priority
            FROM book_fts
            WHERE {col} MATCH :text

            UNION

            SELECT *, 0 AS exact_match_priority
            FROM book_fts
            WHERE {col} LIKE :like_text
            ORDER BY exact_match_priority DESC, {col};
        '''

        results = db.session.execute(
            text(dbquery), {"text": f'"{query}"', "like_text": f"%{query}%"}
        ).fetchall()

        per_page = 10
        paginated_results = results[(page - 1) * per_page : page * per_page]

        total_results = len(results)
        total_pages = (total_results + per_page - 1) // per_page
    """

    query = Book.query

    for column in Book.__table__.columns:
        arg_value = request.args.get(column.name)

        if arg_value:
            query = query.filter(getattr(Book, column.name).like(f"%{arg_value}%"))

    results = query.all()

    page = request.args.get("page", 1, type=int)
    per_page = 10
    results = query.paginate(page=page, per_page=per_page, error_out=False)

    params = request.args.to_dict()
    params.popitem()

    prev_page_url = (
        url_for("search", **params, page=results.page - 1) if results.has_prev else None
    )

    next_page_url = (
        url_for("search", **params, page=results.page + 1) if results.has_next else None
    )

    return render_template(
        "search_results.html",
        args=request.args,
        results=results,
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
    )


@app.route("/advanced_search")
def advanced_search():
    return render_template("advanced_search.html")


@app.route("/book/<book_id>")
def book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return redirect("/")
    return render_template("book.html", book=book)


if __name__ == "__main__":
    app.run(debug=True)
