from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from argon2.exceptions import VerifyMismatchError
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from app import db, login_manager, ph


@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)


class Book(db.Model):
    __tablename__ = "books"

    book_id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    title: Mapped[str] = mapped_column(index=True)
    series: Mapped[Optional[str]] = mapped_column()
    author: Mapped[str] = mapped_column(index=True)
    rating: Mapped[float] = mapped_column(sa.Float)
    description: Mapped[Optional[str]] = mapped_column()
    language: Mapped[str] = mapped_column()
    isbn: Mapped[str] = mapped_column()
    genres: Mapped[str] = mapped_column()
    characters: Mapped[str] = mapped_column()
    book_format: Mapped[Optional[str]] = mapped_column()
    edition: Mapped[Optional[str]] = mapped_column()
    pages: Mapped[Optional[int]] = mapped_column()
    publisher: Mapped[Optional[str]] = mapped_column()
    publish_date: Mapped[Optional[str]] = mapped_column()
    first_publish_date: Mapped[Optional[str]] = mapped_column()
    awards: Mapped[str] = mapped_column()
    num_ratings: Mapped[float] = mapped_column(sa.Float)
    ratings_by_stars: Mapped[str] = mapped_column()
    liked_percent: Mapped[float] = mapped_column(sa.Float)
    setting: Mapped[str] = mapped_column()
    cover_img: Mapped[str] = mapped_column()
    bbe_score: Mapped[int] = mapped_column()
    bbe_votes: Mapped[int] = mapped_column()
    price: Mapped[Optional[float]] = mapped_column(sa.Float)

    # comments: WriteOnlyMapped["Comment"] = relationship(back_populates="book")

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(128), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(sa.String(256))
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    pp: Mapped[str] = mapped_column(sa.String(256), default="uploads/pp/book.png")

    comments: WriteOnlyMapped["Comment"] = relationship(back_populates="user")

    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            ph.verify(self.password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    def __repr__(self):
        return f"<[ID: {self.id}] User {self.username}>"

    def change_pp(self, filepath):
        self.pp = filepath


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str] = mapped_column()
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    # book: Mapped[Book] = relationship(back_populates="comments")
    book_id: Mapped[str] = mapped_column(db.ForeignKey(Book.book_id))

    user: Mapped[User] = relationship(back_populates="comments")
    user_id: Mapped[int] = mapped_column(db.ForeignKey(User.id), index=True)

    def __repr__(self):
        return f'<[ID: {self.id}] Comment "{self.comment}">'

    def date_created_fmt(self, fmt):
        return self.date_created.strftime(fmt)
