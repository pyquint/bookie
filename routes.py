from datetime import datetime

from flask import flash, redirect, render_template, request, session, url_for
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


def register_routes(app, db, ph):
    @app.route("/", methods=["GET", "POST"])
    def index():
        return render_template("index.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        form = SignupForm()

        if form.validate_on_submit():
            username = request.form.get("username")
            email = request.form.get("email")
            password_hash = ph.hash(request.form.get("password"))
            date_created = datetime.now()

            flash(
                f"[{date_created.strftime("%b %d, %Y : %I:%M:%S %p")}]: Account created '{username}'",
                "success",
            )

            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                date_created=date_created.isoformat(),
            )

            db.session.add(user)
            db.session.commit()

            login_user(user)
            session["username"] = username

            return redirect(url_for("index"))

        return render_template("auth/signup.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            form = LoginForm()
            return render_template("auth/login.html", form=form)
        elif request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=User.username).first()

            if user and user.check_password(password):
                login_user(user)
                flash("Logged in successfully.")
                session["username"] = username
                return redirect(url_for("index"))
            else:
                flash("Login unsuccessful.")
                return redirect(url_for("index"))

    @app.route("/logout")
    def logout():
        logout_user()
        flash("Logged out successfully.")
        return redirect(url_for("index"))

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

    @app.route("/user/<username>")
    def user(username):
        user = User.query.filter(User.username == username).first()
        return render_template("user.html", user=user)
