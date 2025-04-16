from datetime import datetime

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app import db
from app.auth import bp
from app.auth.forms import ForgotPasswordForm, LoginForm, SignupForm
from app.models import User


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        date_created = datetime.now()

        flash(
            f"[{date_created.strftime("%b %d, %Y : %I:%M:%S %p")}]: Account created '{username}'",
            "success",
        )

        user = User(
            username=username,
            email=form.email.data,
        )
        user.set_password(form.password.data)

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
        username = form.username.data
        password = form.password.data

        query = sa.select(User).filter_by(username=username)
        user = db.session.scalar(query)

        if user:
            if user.check_password(password):
                login_user(user, remember=form.remember_me.data)
                flash("Logged in successfully.")
                next_redirect = request.form.get("next")
                return redirect(next_redirect)
            else:
                flash("Invalid password.")
            return redirect(url_for("main.index"))
        else:
            flash(f"No such user '{username}'.")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html", form=form)


@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        query = sa.select(User).filter_by(email=email)
        user = db.session.scalar(query)

        if user:
            new_password = form.new_password.data
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
