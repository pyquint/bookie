from datetime import datetime

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app import db, ph
from app.auth import bp
from app.auth.forms import ForgotPasswordForm, LoginForm, SignupForm
from app.models import User


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = request.form.get("username")
        email = request.form.get("email")
        password_plaintext = request.form.get("password")
        password_hash = ph.hash(password_plaintext)
        date_created = datetime.now()

        flash(
            f"[{date_created.strftime("%b %d, %Y : %I:%M:%S %p")}]: Account created '{username}'",
            "success",
        )

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        session["username"] = username

        return redirect(url_for("main.index"))

    return render_template("auth/signup.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")

        query = sa.select(User).filter_by(username=username)
        user = db.session.scalars(query).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get("remember_me"))
            # flash("Logged in successfully.")
            next_redirect = request.form.get("next")
            return redirect(next_redirect)
        else:
            flash("Invalid username or password.")
            return redirect(url_for("main.index"))

    return render_template("auth/login.html", form=form)


@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = request.form.get("email")
        query = sa.select(User).filter_by(email=email)
        user = db.session.scalars(query).first()

        if user:
            new_password = request.form.get("new_password")
            current_user.set_password(new_password)
            db.session.commit()
            render_template("auth/reset_successful.html")
        else:
            print("Incorrect email.")

    return render_template("auth/forgot_password.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("main.index"))


@bp.route("/settings")
@login_required
def settings():
    return render_template("auth/settings.html")
