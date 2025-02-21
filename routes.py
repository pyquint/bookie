from flask import redirect, render_template, request, session, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from forms import LoginForm, SignupForm
from models import Book, User

login_manager = LoginManager()


def register_routes(app, db):
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)

    @app.route("/", methods=["GET", "POST"])
    def index():
        return render_template("index.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        form = SignupForm()
        return render_template("signup.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login(uid):
        form = LoginForm()

        username = request.form["username"]
        password = request.form["password"]
        user = User.query.get(uid)

        if user and user.check_password(password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            pass

        return render_template("login.html", form=form)

    # @app.route("/login/<uid>")
    # def login(uid):
    #     user = User.query.get(uid)
    #     login_user(uid)
    #     return "Successfully logged in"

    @app.route("/logout")
    def logout():
        logout_user()
        return "Successfully logged out"

    @app.route("/search", methods=["GET"])
    def search():
        query = Book.query

        for column in Book.__table__.columns:
            if arg_value := request.args.get(column.name):
                query = query.filter(getattr(Book, column.name).like(f"%{arg_value}%"))

        sort = request.args.get("sort", "title")
        page = request.args.get("page", 1, type=int)
        print("request:", request)

        sorted_query = query.order_by(
            getattr(
                Book, "num_ratings" if sort == "ratings" else sort if sort else "title"
            )
        )
        results = sorted_query.all()

        per_page = 10
        results = sorted_query.paginate(page=page, per_page=per_page, error_out=False)

        params = request.args.to_dict()
        params.pop("page")

        prev_page_url = (
            url_for("search", **params, page=results.page - 1)
            if results.has_prev
            else None
        )

        next_page_url = (
            url_for("search", **params, page=results.page + 1)
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

    @app.route("/advanced_search")
    def advanced_search():
        return render_template("advanced_search.html")

    @app.route("/book/<book_id>")
    def book(book_id):
        book = Book.query.get(book_id)
        if book is None:
            return redirect("/")
        return render_template("book.html", book=book)
