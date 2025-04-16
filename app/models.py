import json
from ast import literal_eval
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from argon2.exceptions import VerifyMismatchError
from flask_login import UserMixin
from sqlalchemy.orm import (
    DynamicMapped,
    Mapped,
    WriteOnlyMapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import TEXT, TypeDecorator

from app import db, login_manager, ph


class ListType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None or value == "":
            return []
        return json.loads(value)


@login_manager.user_loader
def load_user(id):
    return db.session.get(User, id)


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    series: Mapped[Optional[str]] = mapped_column()
    author: Mapped[str] = mapped_column(index=True)
    rating: Mapped[float] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    language: Mapped[str] = mapped_column()
    isbn: Mapped[str] = mapped_column()
    genres: Mapped[str] = mapped_column(index=True)
    characters: Mapped[str] = mapped_column()
    book_format: Mapped[Optional[str]] = mapped_column()
    edition: Mapped[Optional[str]] = mapped_column()
    pages: Mapped[Optional[int]] = mapped_column()
    publisher: Mapped[Optional[str]] = mapped_column()
    publish_date: Mapped[Optional[str]] = mapped_column()
    first_publish_date: Mapped[Optional[str]] = mapped_column()
    awards: Mapped[str] = mapped_column()
    num_ratings: Mapped[float] = mapped_column()
    ratings_by_stars: Mapped[str] = mapped_column()
    liked_percent: Mapped[float] = mapped_column()
    setting: Mapped[str] = mapped_column()
    cover_img: Mapped[str] = mapped_column()
    bbe_score: Mapped[int] = mapped_column()
    bbe_votes: Mapped[int] = mapped_column()
    price: Mapped[Optional[float]] = mapped_column()

    comments: DynamicMapped[list["Comment"]] = relationship(back_populates="book")
    favorited_by: Mapped[list["User"]] = relationship(secondary="user_favorites")
    book_statuses: WriteOnlyMapped[list["BookStatus"]] = relationship(
        back_populates="book", lazy="dynamic"
    )

    def get_status_for(self, user_id):
        if user_id:
            print(f"{user_id=}, {self.id=}")
            status = db.session.get(BookStatus, (user_id, self.id))
            return status
        else:
            return None

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"

    def get_genres(self):
        return literal_eval(self.genres) if self.genres else []

    def add_genre(self, genre):
        genres = self.get_genres()
        if genre not in genres:
            genres.append(genre)
            self.genres = str(genres)

    def remove_genre(self, genre):
        genres = self.get_genres()
        if genre in genres:
            genres.remove(genre)
            self.genres = str(genres)

    def get_characters(self):
        return literal_eval(self.characters) if self.characters else []

    def add_character(self, character):
        characters = self.get_characters()
        if character not in characters:
            characters.append(character)
            self.characters = str(characters)

    def remove_character(self, character):
        characters = self.get_characters()
        if character in characters:
            characters.remove(character)
            self.characters = str(characters)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(128), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(256))
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    pp: Mapped[str] = mapped_column(sa.String(256), default="uploads/pp/book.png")

    comments: WriteOnlyMapped["Comment"] = relationship(
        back_populates="user", lazy="dynamic"
    )
    book_statuses: Mapped[list["BookStatus"]] = relationship(
        back_populates="user", lazy="dynamic"
    )
    favorite_books: Mapped[list["Book"]] = relationship(
        secondary="user_favorites", lazy="dynamic"
    )

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

    def change_pp(self, filepath):
        self.pp = filepath

    def get_book_status(self, book_id):
        status = db.session.get(BookStatus, (self.id, book_id))
        return status

    def __repr__(self):
        return f"<User {self.id} {self.username}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str] = mapped_column()
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    book: Mapped[Book] = relationship(back_populates="comments")
    book_id: Mapped[str] = mapped_column(db.ForeignKey(Book.id))

    user: Mapped[User] = relationship(back_populates="comments")
    user_id: Mapped[int] = mapped_column(db.ForeignKey(User.id), index=True)

    def __repr__(self):
        return f'<Comment {self.id} "{self.comment}">'

    def date_created_fmt(self, fmt):
        return self.date_created.strftime(fmt)


class ReadingStatus(db.Model):
    __tablename__ = "reading_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(128), unique=True)

    book_statuses: Mapped[list["BookStatus"]] = relationship(
        back_populates="reading_status", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Reading Status {self.id} '{self.name}'>"


class BookStatus(db.Model):
    __tablename__ = "book_statuses"

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey(User.id), primary_key=True, autoincrement=False
    )
    book_id: Mapped[int] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )
    reading_status_id: Mapped[int] = mapped_column(db.ForeignKey(ReadingStatus.id))
    finished_chapters: Mapped[int] = mapped_column(default=0)

    reading_status: Mapped[ReadingStatus] = relationship(back_populates="book_statuses")
    user: Mapped[User] = relationship(back_populates="book_statuses")
    book: Mapped[Book] = relationship(back_populates="book_statuses")

    def __repr__(self):
        return f"<BookStatus {self.user}, {self.book}, {self.reading_status}, {self.finished_chapters}>"


class UserFavorite(db.Model):
    __tablename__ = "user_favorites"

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey(User.id), primary_key=True, autoincrement=False
    )
    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )

    # def __repr__(self):
    #     return f"<UserFavorite {self.user.id}, {self.book.id}"
    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )

    # def __repr__(self):
    #     return f"<UserFavorite {self.user.id}, {self.book.id}"
